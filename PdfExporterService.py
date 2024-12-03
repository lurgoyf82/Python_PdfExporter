import sys
import servicemanager
import win32serviceutil

from classes.pdfExporterService import PdfExporterService


def run_service():
    servicemanager.Initialize()
    servicemanager.PrepareToHostSingle(PdfExporterService)
    servicemanager.StartServiceCtrlDispatcher()


def handle_command_line():
    win32serviceutil.HandleCommandLine(PdfExporterService)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        try:
            run_service()
        except Exception as e:
            print('An error occurred: {0}'.format(e))
    else:
        # Command-line options
        handle_command_line()
