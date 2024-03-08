import multiprocessing
import subprocess


class InkscapeWorker(multiprocessing.Process):
    def __init__(self, queue, log=False):
        super(InkscapeWorker, self).__init__()
        self.queue = queue
        self.log = log

    def wait_for_inkscape(self):
        while(True):
            char = self.ink.stdout.read(1)
            if(self.log):
                try:
                    print(char.decode('utf-8'),end='')
                except UnicodeDecodeError:
                    print(char)
            if char == b'>':
                break

    def run(self):
        # this is our inkscape worker
        self.ink = subprocess.Popen(['inkscape', '--shell'],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

        # first, wait for inkscape startup
        self.wait_for_inkscape()

        for svg_file, pdf_file_name, cached in iter(self.queue.get, None):

            # main working loop of the inkscape process
            # we need to wait for ">" to see whether inkscape is ready.
            # The variable ready keeps track of that.

            if not cached:
                command = f'file-open:{svg_file}; export-filename:{pdf_file_name}; export-type:pdf; export-do;\n'
                self.ink.stdin.write(command.encode("UTF-8"))
                self.ink.stdin.flush()

                self.wait_for_inkscape()

                print("  Converted {0}".format(pdf_file_name))
            else:
                print("  Skipping {0}".format(pdf_file_name))

