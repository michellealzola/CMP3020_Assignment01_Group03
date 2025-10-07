from __future__ import annotations

import sys

from typing import List, Tuple, Optional
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QRectF
from PySide6.QtGui import QIcon, QPixmap, QFont, QFontDatabase, QPainter, QTextCursor, QTextCharFormat, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QTextEdit, QLineEdit, QLabel, QFileDialog, QMessageBox, QPlainTextEdit, QSplitter,
    QTableWidget, QSizePolicy, QTableWidgetItem, QHeaderView,
)

# SVG Renderer
try:
    from PySide6.QtSvg import QSvgRenderer  # type: ignore
    _SVG_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    QSvgRenderer = None  # type: ignore[assignment]
    _SVG_AVAILABLE = False

from LexicalAnalyzer import LexicalAnalyzer, Token, TokenRow
from SyntaxAnalyzer import SyntaxAnalyzer, ParseError

DEFAULT_SAMPLE = '''\
list = [1, 2, 3]
sum = 0
count = 0

if len(list) != 0:
    for n in list:
        sum += n
        count += 1
    endfor
    
    average = (sum / count) if count != 0 else 0
    print('The average of the list is', average)
else:
    print('The list is empty.')
endif
'''

TABLE_LABELS = ['Lexeme', 'Token', 'Explanation']

# to make file-relative paths
def _here() -> Path:  # returns a pathlib.path
    base = getattr(sys, '_MEIPASS', None)
    return Path(base) if base else Path(__file__).parent.resolve()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Serpent+ Code Analyzer')
        self.resize(1200, 1000)

        # favicon for window
        self.apply_window_icon(
            _here() / 'serpent_plus_favicon.svg',
            fallback_svg=_here() / 'serpent_plus_logo.svg'
        )

        # LEFT PANEL: Header with Logo and title, editor textbox, and Analyze and Reset buttons
        left_panel = QWidget()
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(10, 10, 10, 10)
        left_panel_layout.setSpacing(10)

        # Header Horizontal Box
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        self.logo_label = QLabel()
        self._set_logo(self.logo_label, _here() / 'serpent_plus_logo.svg', target_height=50)

        title_label = QLabel('Code Analyzer')
        title_label.setStyleSheet(f'''
            font-size: 20px;
            font-weight: 500;

        ''')

        header_layout.addWidget(self.logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)

        # Editor / Code Text Box
        self.edit_code = QTextEdit()
        self.edit_code.setPlaceholderText('Type Serpent+ code here...')
        self.edit_code.setPlainText(DEFAULT_SAMPLE)
        self.edit_code.setLineWrapMode(QTextEdit.NoWrap)
        self._apply_code_font(self.edit_code, _here() / 'NanumGothicCoding-Regular.ttf')

        # Analyze and Reset Buttons
        button_box = QHBoxLayout()
        self.analyze_button = QPushButton('Analyze')
        self.analyze_button.setMinimumWidth(150)
        self.analyze_button.setMinimumHeight(50)
        self.analyze_button.setStyleSheet('''
            QPushButton {
                font-size: 16px;
            }
        ''')
        self.reset_button = QPushButton('Reset')
        self.reset_button.setMinimumWidth(150)
        self.reset_button.setMinimumHeight(50)
        self.reset_button.setStyleSheet('''
            QPushButton {
                font-size: 16px;
            }
        ''')

        self.docs_link = QLabel('<a href="https://github.com/michellealzola/CMP3020_Assignment01_Group03/blob/master/PartC/serpent_language_documentation.md">Serpent+ Language Documentation</a>')
        self.docs_link.setStyleSheet('''
            QLabel{
                font-size: 18px;
            }
        ''')
        self.docs_link.setTextFormat(Qt.RichText)
        self.docs_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.docs_link.setOpenExternalLinks(True)
        self.docs_link.setCursor(Qt.PointingHandCursor)

        button_box.addWidget(self.analyze_button)
        button_box.addWidget(self.reset_button)
        button_box.addStretch()
        button_box.addWidget(self.docs_link)

        left_panel_layout.addWidget(header)
        left_panel_layout.addWidget(self.edit_code)
        left_panel_layout.addLayout(button_box)

        # RIGHT PANEL: Tokenization Table
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(10, 10, 10, 10)
        right_panel_layout.setSpacing(10)

        table_label = QLabel('Tokenization Table')
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(TABLE_LABELS)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        right_panel_layout.addWidget(table_label)
        right_panel_layout.addWidget(self.table, 1)

        # To have a resize handle between the left and right panels
        split = QSplitter(Qt.Horizontal)
        split.addWidget(left_panel)
        split.addWidget(right_panel)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 1)
        self.setCentralWidget(split)

        # Status box
        self.status_label = QLabel('')
        self.statusBar().addWidget(self.status_label)

        # Button clicked connections
        self.analyze_button.clicked.connect(self.on_analyze)
        self.reset_button.clicked.connect(self.on_reset)

    def apply_window_icon(self, primary_svg: Path, fallback_svg: Optional[Path] = None) -> None:
        sizes = [16, 24, 32, 48, 64, 128, 256]
        icon = self._make_icon_from_svg(primary_svg, sizes)
        if icon is None and fallback_svg is not None:
            icon = self._make_icon_from_svg(fallback_svg, sizes)
        if icon is not None:
            self.setWindowIcon(icon)
            QApplication.setWindowIcon(icon)

    def _set_logo(self, label: QLabel, svg_path: Path, target_height: int = 28) -> None:
        if svg_path.exists() and _SVG_AVAILABLE:
            renderer = QSvgRenderer(str(svg_path))
            renderer_size = renderer.defaultSize()
            if not renderer_size.isValid():
                renderer_size = QSize(256, 64)
            aspect_ratio = renderer_size.width() / max(1, renderer_size.height())
            width = max(1, int(round(target_height * aspect_ratio)))
            height = target_height

            pix_map = QPixmap(width, height)
            pix_map.fill(Qt.transparent)

            painter = QPainter(pix_map)
            painter.setRenderHint(QPainter.Antialiasing, True)
            renderer.render(painter, QRectF(0, 0, width, height))
            painter.end()

            label.setPixmap(pix_map)
            label.setFixedSize(pix_map.size())
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        else:
            label.setText('Serpent+')
            label.setStyleSheet('font-size: 20px; font-weight: 500;')

    def _apply_code_font(self, widget: QWidget, font_path: Path) -> None:
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                font = QFont(font_families[0], 12)
                font.setStyleHint(QFont.Monospace)
            else:
                font = QFont('Courier New', 12)
        else:
            font = QFont('Courier New', 12)
        widget.setFont(font)

    def on_analyze(self) -> None:
        src = self.edit_code.toPlainText()

        # Lexical Analysis
        base = _here()
        try:
            lexer = LexicalAnalyzer(
                keyword_path=str(base / 'keywords.txt'),
                builtin_path=str(base / 'builtin.txt'),
                token_lexeme_path=str(base / 'token_lexeme.txt'),
                token_translation_path=str(base / 'token_translation.txt'),
            )
        except Exception as e:
            self._show_error(
                'Failed to initialize LexicalAnalyzer.\n'
                'Ensure token_lexeme.txt, token_translation.txt,\n'
                'keywords.txt, and builtin.txt are present.\n\n'
                f'{e}'
            )
            return

        try:
            tokens, lex_errors = lexer.tokenize(src)
        except Exception as e:
            self._show_error(
                'Failed to tokenize source code.\n\n'
            )
            return

        if lex_errors:
            self._show_error(
                'Lexical errors:\n\n' + '\n'.join(f' - {e}' for e in lex_errors)
            )
            self._populate_table([])
            self._set_status('Lexical errors detected.', ok=False)

        rows = lexer.tokens_table(tokens)
        self._populate_table(rows)
        self._set_status('Lexical analysis complete.', ok=True)

        # Syntax Analysis
        try:
            syn = SyntaxAnalyzer(
                tokens,
                block_termination_path=str(base / 'block_termination.txt'),
            )
            syn.parse_program()
            self._set_status('Syntax analysis complete.', ok=True)
            self.edit_code.setExtraSelections([])
        except ParseError as e:
            self._set_status(f'Syntax errors detected: {e}', ok=False)
            self._highlight_error_line(getattr(e, 'line', 1))
            QMessageBox.critical(self, 'Syntax Error', str(e))

    def on_reset(self) -> None:
        self.edit_code.clear()
        self.table.setRowCount(0)
        self.status_label.setText('')
        self.statusBar().showMessage('')

    def _make_icon_from_svg(self, svg_path: Path, sizes: List[int]) -> Optional[QIcon]:
        if not (svg_path.exists() and _SVG_AVAILABLE):
            return None

        renderer = QSvgRenderer(str(svg_path))
        size = renderer.defaultSize()
        if not size.isValid():
            size = QSize(256, 256)

        icon = QIcon()
        aspect_ratio = size.width() / max(1, size.height())

        for sz in sizes:
            pix_map = QPixmap(sz, sz)
            pix_map.fill(Qt.transparent)

            if aspect_ratio >= 1.0:
                width = sz
                height = max(1, int(round(sz / aspect_ratio)))
            else:
                width = max(1, int(round(sz * aspect_ratio)))
                height = sz
            x = (sz - width) // 2
            y = (sz - height) // 2

            painter = QPainter(pix_map)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            renderer.render(painter, QRectF(x, y, width, height))
            painter.end()

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, 'Error', message)

    def _populate_table(self, rows: List[TokenRow]) -> None:
        self.table.setRowCount(len(rows))
        for row, (lexeme, token_name, explanation) in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(lexeme))
            self.table.setItem(row, 1, QTableWidgetItem(token_name))
            self.table.setItem(row, 2, QTableWidgetItem(explanation))
        self.table.resizeColumnsToContents()

    def _set_status(self, text: str, ok: bool = True) -> None:
        self.statusBar().showMessage(text)
        color = '#2e7d32' if ok else '#c62828'
        self.status_label.setStyleSheet(f'color: {color}; font-weight: 600;')
        self.status_label.setText(text)

    def _highlight_error_line(self, line: int) -> None:
        self.edit_code.setExtraSelections([])

        selection = QTextEdit.ExtraSelection()
        frmt = QTextCharFormat()
        frmt.setBackground(QColor('#ffecec'))
        selection.format = frmt

        cursor = self.edit_code.textCursor()
        cursor.movePosition(QTextCursor.Start)
        if line > 1:
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line - 1)
        cursor.select(QTextCursor.LineUnderCursor)
        selection.cursor = cursor

        self.edit_code.setExtraSelections([selection])
        self.edit_code.setTextCursor(cursor)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())