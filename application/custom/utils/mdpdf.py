from io import BytesIO
from markdown_pdf import MarkdownPdf, Section



class MdPDF:

    @staticmethod
    def pdf_from_md(md_text:str) -> BytesIO:
        """Create a PDF file from md formatted text

        Args:
            md_text (str): Markdown content

        Returns:
            BytesIO: PDF file
        """

        pdf = MarkdownPdf()
        pdf.add_section(Section(md_text, toc=False))

        pdf_buffer = BytesIO()
        pdf.save(pdf_buffer)
        pdf_buffer.seek(0)

        return pdf_buffer