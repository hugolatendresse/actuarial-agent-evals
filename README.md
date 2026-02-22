# aria-tests

Test harness for actuarial methods: runs unit tests (step-by-step) and integration tests (full run) against AI coding assistants (Cursor, Cline, Continue).

**Prerequisites:** Python 3, `pip install -r requirements.txt`

**Support:** Tested on macOS and Linux (Ubuntu 24.04). Automation may not work on other OSes; tests can still be run in manual mode.

### Manual vs auto mode

- **Manual:** You copy prompts and paste them into the chatbot.
- **Auto:** Prompts are sent to the chatbot automatically. The goal is a fully unattended run; in practice the chat may hang or need a nudge to finish.

### Run all tests

`launch_all_tests.py` — run every unit test or every integration test.

```bash
python launch_all_tests.py --ide cline --mode auto --test-type integration
python launch_all_tests.py --ide cursor --mode manual --test-type unit
```

Required: `--ide` (e.g. `cursor`, `cline`, `continue`), `--mode` (`auto` or `manual`), `--test-type` (`integration` or `unit`).

### Available tests

**Integration tests** (one full task per method):

| Method | Unit steps |
|--------|------------|
| `friedland_xyz_bf_method` | 2 |
| `friedland_xyz_cc_method` | 5 |
| `friedland_xyz_fs1_method` | 5 |
| `friedland_xyz_dev_method` | 6 |
| `werner_modlin_b` | 7 |
| `friedland_xyz_fs3_method` | 10 |
| `friedland_xyz_fs2_method` | 12 |
| `werner_modlin_a` | 14 |

**Unit tests** run the same methods step-by-step: each integration test is broken into the number of steps above. Use unit tests to run a single step or a range of steps (e.g. `--step step_1` or `--start-from step_2`).

### Run one unit test

`launch_one_unit_test.py` — run a single method’s unit test (optionally from a step or a single step).

```bash
python launch_one_unit_test.py --method friedland_xyz_bf_method --ide cline --mode auto
python launch_one_unit_test.py --method friedland_xyz_bf_method --ide cline --mode manual --step step_1
python launch_one_unit_test.py --method werner_modlin_b --ide cline --mode auto --start-from step_2
```

Required: `--method`, `--ide`. Optional: `--mode` (default `manual`), `--start-from`, `--step`.

### Run one integration test

`launch_one_integration_test.py` — run one method’s integration test, or all methods. Shortest run: `friedland_xyz_bf_method` (2 steps).

```bash
python launch_one_integration_test.py --method friedland_xyz_bf_method --ide cline --mode auto
python launch_one_integration_test.py --method all --ide cline --mode auto
```

Required: `--method` (method name or `all`), `--ide`. Optional: `--mode` (default `manual`).

Methods are discovered from the `methods/` directory; pass an unknown `--method` to see the list.
