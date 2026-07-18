import fitz  # PyMuPDF
from loguru import logger
from typing import List, Tuple
from app.domain.parser.models import ParsedBlock, DocumentPayload, BoundingBox
from app.models.relational import NodeType
import numpy as np
import cv2

class ParserException(Exception):
    pass

class CorruptPDFError(ParserException):
    def __init__(self, message="Corrupt or invalid PDF file."):
        super().__init__(message)

class DocumentParser:
    def __init__(self, char_density_threshold: float = 0.001):
        self.char_density_threshold = char_density_threshold
        self._ocr_engine = None
        self._pp_structure = None

    def _get_ocr_engine(self):
        if not self._ocr_engine:
            logger.info("Initializing PaddleOCR...")
            from paddleocr import PaddleOCR, PPStructure
            self._ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            self._pp_structure = PPStructure(show_log=False)
        return self._ocr_engine, self._pp_structure

    def process_pdf(self, file_path: str) -> DocumentPayload:
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise CorruptPDFError(f"Failed to open PDF: {e}")

        all_blocks = []
        raw_layouts = []
        raw_ocr = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            rect = page.rect
            page_area = rect.width * rect.height
            if page_area <= 0:
                continue

            # 2. Extract native digital text
            text_instances = page.get_text("dict")["blocks"]
            native_chars = 0
            native_blocks = []

            for b in text_instances:
                if b["type"] == 0:  # Text block
                    text_content = ""
                    for l in b["lines"]:
                        for s in l["spans"]:
                            text_content += s["text"]
                            native_chars += len(s["text"].strip())
                    
                    if text_content.strip():
                        bbox = BoundingBox(x0=b["bbox"][0], y0=b["bbox"][1], x1=b["bbox"][2], y1=b["bbox"][3])
                        font_size = b["lines"][0]["spans"][0]["size"] if b["lines"] and b["lines"][0]["spans"] else None
                        native_blocks.append(
                            ParsedBlock(
                                text=text_content.strip(),
                                bbox=bbox,
                                page_number=page_num + 1,
                                is_native_text=True,
                                font_size=font_size
                            )
                        )

            # 3. Decision heuristic
            char_density = native_chars / page_area
            logger.info(f"Page {page_num + 1} char density: {char_density}")

            if char_density > self.char_density_threshold:
                # Usable digital text layer, skip OCR
                logger.info(f"Page {page_num + 1}: Skipping OCR (native text found)")
                all_blocks.extend(native_blocks)
            else:
                # 4. Run PP-Structure & PaddleOCR
                logger.info(f"Page {page_num + 1}: Running OCR")
                ocr, pp = self._get_ocr_engine()
                
                # Render page to image
                pix = page.get_pixmap()
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                if pix.n == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                elif pix.n == 1:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

                # layout
                layout_res = pp(img)
                raw_layouts.append({"page_number": page_num + 1, "layout": layout_res})
                
                # ocr
                ocr_res = ocr.ocr(img, cls=True)
                raw_ocr.append({"page_number": page_num + 1, "ocr": ocr_res})
                
                if ocr_res and ocr_res[0]:
                    for line in ocr_res[0]:
                        box = line[0]
                        txt = line[1][0]
                        conf = line[1][1]
                        
                        xs = [p[0] for p in box]
                        ys = [p[1] for p in box]
                        
                        bbox = BoundingBox(x0=min(xs), y0=min(ys), x1=max(xs), y1=max(ys))
                        
                        all_blocks.append(
                            ParsedBlock(
                                text=txt,
                                bbox=bbox,
                                page_number=page_num + 1,
                                is_native_text=False,
                                confidence=conf
                            )
                        )

        # 5 & 6. Merge & Reconstruct reading order
        all_blocks.sort(key=lambda b: (b.page_number, round(b.bbox.x0 / 100), b.bbox.y0))
        for idx, b in enumerate(all_blocks):
            b.reading_order_index = idx

        # 7. Classify each block
        self._classify_blocks(all_blocks)

        # 8. Drop repeated headers/footers
        all_blocks = self._drop_headers_footers(all_blocks)

        # 10. Validate
        self._validate_blocks(all_blocks)

        doc.close()
        return DocumentPayload(blocks=all_blocks, raw_layouts=raw_layouts, raw_ocr=raw_ocr)

    def _classify_blocks(self, blocks: List[ParsedBlock]):
        for b in blocks:
            if b.font_size and b.font_size > 16:
                b.node_type = NodeType.heading
                b.heading_level = 1
            elif b.font_size and b.font_size > 14:
                b.node_type = NodeType.heading
                b.heading_level = 2
            elif b.font_size and b.font_size > 12:
                b.node_type = NodeType.heading
                b.heading_level = 3
            else:
                b.node_type = NodeType.paragraph
                
            if not b.font_size:
                b.node_type = NodeType.paragraph

    def _drop_headers_footers(self, blocks: List[ParsedBlock]) -> List[ParsedBlock]:
        top_y_blocks = {}
        for b in blocks:
            if b.bbox.y0 < 50:
                top_y_blocks[b.text] = top_y_blocks.get(b.text, 0) + 1
                
        kept_blocks = []
        for b in blocks:
            if b.bbox.y0 < 50 and top_y_blocks.get(b.text, 0) > 2:
                logger.info(f"Dropped repeated header: {b.text}")
                continue
            kept_blocks.append(b)
            
        for idx, b in enumerate(kept_blocks):
            b.reading_order_index = idx
            
        return kept_blocks

    def _validate_blocks(self, blocks: List[ParsedBlock]):
        for i in range(1, len(blocks)):
            if blocks[i].reading_order_index <= blocks[i-1].reading_order_index:
                raise ParserException("Non-monotonic reading order detected.")
            if not blocks[i].bbox:
                raise ParserException("Orphan block without bounding box detected.")
