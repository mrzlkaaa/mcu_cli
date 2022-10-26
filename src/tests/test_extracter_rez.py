import pytest
import os
import asyncio
from collections import defaultdict
from handler.extracter_rez import Rez

dd:defaultdict = {
        # '/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/rez': ['5001_mini.REZ', '5002_mini.REZ', '5004_mini.REZ', '!5002_mini.REZ']
        '/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/rez': ['!5002_mini.REZ']
        }

dd_export = {
    'rez': 
        {
        '!5002_mini.REZ':
            {
            '0-th block': 
                {
                'Material 2. FULL ISOTOPE LIST.': 
                {
                    'Time': ['0.0', '220.0'], 
                    'Sum': ['1.751E-08', '1.821E-08'], 
                    'Ra-226': ['1.751E-08', '1.519E-08'], 
                    'Th-228': ['0.000E+00', '1.205E-09'], 
                    'He-  4': ['0.000E+00', '7.211E-10'], 
                    'Ac-227': ['0.000E+00', '5.763E-10'], 
                    'Th-229': ['0.000E+00', '3.008E-10'], 
                    'Pb-208': ['0.000E+00', '1.392E-10']
                }, 
                'Material 2. SELECTED ISOTOPES. NUCLEAR': 
                {
                    'Time': ['0.0', '5.0', '10.0', '15.0', '17.5', '20.0', '22.5', '25.0', '30.0', '35.0', '40.0'], 
                    'Sum': ['1.751E-08', '1.752E-08', '1.752E-08', '1.752E-08', '1.751E-08', '1.751E-08', '1.751E-08', '1.750E-08', '1.749E-08', '1.747E-08', '1.745E-08'], 
                    'Ra-226': ['1.751E-08', '1.723E-08', '1.696E-08', '1.668E-08', '1.654E-08', '1.641E-08', '1.628E-08', '1.615E-08', '1.589E-08', '1.564E-08', '1.539E-08'],
                    'Ac-225': ['0.000E+00', '5.076E-15', '1.513E-14', '2.646E-14', '3.215E-14', '3.773E-14', '4.314E-14', '4.833E-14', '5.805E-14', '6.686E-14', '7.476E-14'], 
                    'Ac-226': ['0.000E+00', '1.028E-15', '3.052E-15', '5.340E-15', '6.487E-15', '7.614E-15', '8.736E-15', '9.786E-15', '1.176E-14', '1.354E-14', '1.514E-14'], 
                    'Ac-227': ['0.000E+00', '2.067E-10', '3.189E-10', '3.785E-10', '3.957E-10', '4.074E-10', '4.134E-10', '4.156E-10', '4.158E-10', '4.129E-10', '4.084E-10'], 
                    'Ac-228': ['0.000E+00', '9.412E-12', '1.447E-11', '1.718E-11', '1.796E-11', '1.849E-11', '1.882E-11', '1.892E-11', '1.893E-11', '1.880E-11', '1.859E-11'], 
                    'Th-227': ['0.000E+00', '3.382E-14', '8.133E-14', '1.163E-13', '1.284E-13', '1.374E-13', '1.438E-13', '1.479E-13', '1.519E-13', '1.527E-13', '1.521E-13'],
                    'Th-228': ['0.000E+00', '6.701E-11', '2.163E-10', '3.995E-10', '4.950E-10', '5.901E-10', '6.835E-10', '7.736E-10', '9.420E-10', '1.094E-09', '1.229E-09'],
                    'Th-229': ['0.000E+00', '2.147E-12', '1.420E-11', '4.008E-11', '5.843E-11', '8.021E-11', '1.053E-10', '1.334E-10', '1.973E-10', '2.695E-10', '3.476E-10'], 
                    'Th-230': ['0.000E+00', '3.840E-14', '5.267E-13', '2.295E-12', '3.951E-12', '6.274E-12', '9.351E-12', '1.328E-11', '2.402E-11', '3.903E-11', '5.864E-11']
                }
                }
            }
        }
    }

@pytest.fixture
def rez():
    return Rez(dd, "all")

@pytest.mark.asyncio
async def test_data_extraction(rez):
    rez.data_blocks["rez"] = defaultdict(list)
    await rez.data_extraction("/mnt/c/Users/Nikita/Desktop/codes/mcu_code_runner/src/test_data/rez", "rez", ["!5002_mini.REZ"])
    print(rez.data_blocks)
    assert 0

def test_data_export(rez):
    rez.data_block = dd_export
    rez.data_excel_export()

@pytest.mark.asyncio
async def test_run(rez):
    await rez.run()
    assert 0