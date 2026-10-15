LAB 3 Report: SZZ Tracing

SWAPD 451 - Software Maintenance

Name: Nada Waleed Mohamed ID: 202301334

Repository: https://github.com/naadaaa/maintenance-issues-lab (branch: fix-login-bug)

SZZ Results
Bug Fixing Commit (BFC)	File	Script Bug Inducing Commit (BIC) (normal blame)	Script BIC (-C -C)	Result
2d48f81	auth.py	d834aa3	b186621	-C -C found the true origin
d5fecdf	login.html	none (ghost commit)	none	N/A
Normal blame vs git blame -C -C

The first commit shows that normal git blame attributed the buggy line to a commit that moved the code into auth.py. Using git blame -C -C traced it back to b186621 in helpers.py, where it originally appeared.

The second commit added 31 lines without deleting any existing lines. Since the script traces deleted lines, it could not identify a bug-introducing commit and classified the change as a ghost commit.

Source Code & Screenshots

szz_tracer.py (in the submission ZIP file and in the repository: https://github.com/naadaaa/maintenance-issues-lab/blob/fix-login-bug/szz_tracer.py)

Screenshots are in the ZIP file as well.