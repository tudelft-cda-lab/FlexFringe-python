import subprocess
import shutil
import time
from pathlib import Path
from PIL import Image
import graphviz as graphviz
import io
import pandas as pd

class FlexFringe:
    def __init__(self, flexfringe_path=None):

        if flexfringe_path is None:
            self.path = shutil.which("flexfringe")
        else:
            self.path = flexfringe_path

        if self.path is None:
            raise RuntimeError(
                "Could not find flexfringe executable. Please put it in your PATH or provide flexfringe_path in the constructor")

        self.tracefile = None
        self.resultfile = None

    @property
    def dot_out(self) -> Path:
        return self._get_out_file(".ff.final.dot")

    @property
    def json_out(self) -> Path:
        return self._get_out_file(".ff.final.json")

    @property
    def result_out(self) -> Path:
        return self._get_out_file(".ff.final.json.result")

    def _get_out_file(self, extension: str) -> Path:
        if self.tracefile is None:
            raise RuntimeError("No tracefile specified. Please first run \"fit\"")

        tmp = Path(f"{self.tracefile}{extension}")

        if not tmp.exists() or not tmp.is_file():
            raise RuntimeError(f"Could not find valid flexfringe output file at: {str(tmp)}")

        return tmp

    def fit(self, tracefile, heuristic_name="alergia", data_name="alergia_data", **kwargs):
        kwargs["heuristic_name"] = heuristic_name
        kwargs["data_name"] = data_name
        flags = self._format_kwargs(**kwargs)

        command = [tracefile] + flags

        self._run(command)

        self.tracefile = tracefile

        try:
            with self.dot_out.open('r') as fh:
                dot_content = fh.read()
            with self.json_out.open('r') as fh:
                json_content = fh.read()
        except FileNotFoundError as e:
            raise RuntimeError(f"Error running FlexFringe: no output file found: {e.filename}")

    def predict(self, tracefile, heuristic_name="alergia", data_name="alergia_data", **kwargs):
        kwargs["heuristic_name"] = heuristic_name
        kwargs["data_name"] = data_name
        flags = self._format_kwargs(**kwargs)

        command = [tracefile, "--mode=predict", f"--aptafile={self.json_out}"] + flags

        self._run(command)

        return self._parse_flexfringe_result()

    def _parse_flexfringe_result(self):
        df = pd.read_csv(self.result_out, delimiter=";", index_col="row nr")
        df.columns = [column.strip() for column in df.columns]

        # Parse abbadingo traces
        abd_traces = df['abbadingo trace']
        abd_traces = abd_traces.apply(lambda x: x.strip().strip("\""))

        abd_type = []
        abd_len = []
        abd_trc = []

        for abd_trace in abd_traces:
            parts = abd_trace.split(" ")
            abd_type.append(parts[0])
            abd_len.append(parts[1])
            abd_trc.append(parts[2:])

        df = df.drop(columns=["abbadingo trace"])
        df.insert(0, "abbadingo type", abd_type)
        df.insert(1, "abbadingo length", abd_len)
        df.insert(2, "abbadingo trace", abd_trace)

        # Parse state sequences
        df['state sequence'] = df['state sequence']\
            .apply(lambda x: x.strip().strip("[").strip("]").split(","))

        # Parse score sequence
        df['score sequence'] = df['score sequence']\
            .apply(lambda x: [float(val) for val in x.strip().strip("[").strip("]").split(",")])

        # And the rest of the score columns
        df['sum scores'] = df['sum scores'].astype(float)
        df['mean scores'] = df['mean scores'].astype(float)
        df['min score'] = df['min score'].astype(float)

        return df

    def _run(self, command=None):
        """
        Wrapper to call the flexfringe binary
        """

        if command is None:
            command = ["--help"]

        full_cmd = ["flexfringe"] + command
        print("Running: ", " ".join(full_cmd))
        result = subprocess.run([self.path] + command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, universal_newlines=True)
        print(result.returncode, result.stdout, result.stderr)

    def show(self, format="png"):
        """
        Renders the final state machine generated by flexfringe using graphviz
        and displays it using pillow.

        :param format: a file format supported by both graphviz and pillow.
        """
        if self.dot_out is None:
            raise RuntimeError("No output available, run \"fit\" first")
        else:
            with Path(self.dot_out).open('r') as in_file:
                g = graphviz.Source(
                    in_file.read()
                )

            data = io.BytesIO()
            data.write(g.pipe(format=format))
            data.seek(0)

            img = Image.open(data)
            img.show()

            # Need to give it time to open image viewer :/
            time.sleep(1)

    def _format_kwargs(self, **kwargs):
        """
        Turns kwargs into a list of command line flags that flexfringe understands
        :param kwargs: the kwargs to translate
        :return: a list of command line args for flexfringe
        """
        flags = []
        for key in kwargs:
            flags += ["--" + key + "=" + kwargs[key]]
        return flags


