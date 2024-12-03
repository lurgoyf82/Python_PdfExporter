from cx_Freeze import setup, Executable

# Replace 'your_script.py' with your main Python script
setup(
    name="PdfExporter",
    version="1.0",
    description="PDF Exporter Application",
    executables=[Executable("PdfExporterService.py")]
)
