import qrotor as qr
import os
import shutil


#gridsizes = [1000, 2000, 3000, 5000, 10000, 15000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 125000, 150000, 175000, 200000, 250000, 300000, 400000, 500000]
gridsizes = [1000, 2000, 3000]

script_name = 'convergence_calc.py'
script_file = os.path.join(os.getcwd(), script_name)

slurm_name = 'convergence.slurm'
slurm_file = os.path.join(os.getcwd(), slurm_name)

for gridsize in gridsizes:
    slurm_copy_name = f'temp_{gridsize}.slurm'
    slurm_copy = os.path.join(os.getcwd(), slurm_copy_name)
    shutil.copy(slurm_file, slurm_copy)

    script_copy_name = f'temp_{gridsize}.py'
    script_copy = os.path.join(os.getcwd(), script_copy_name)
    shutil.copy(script_file, script_copy)

    qr.file.replace_line_with_keyword(f'#SBATCH --job-name=QRotor_{gridsize}', '#SBATCH --job-name=', slurm_copy)
    qr.file.replace_line_with_keyword(f'python3 {script_copy_name}', 'python3 ', slurm_copy)

    qr.file.replace_line_with_keyword(f'this_script_is_a_copy=True', 'this_script_is_a_copy=', script_copy)
    qr.file.replace_line_with_keyword(f'gridsize={gridsize}', 'gridsize=', script_copy)
    qr.file.replace_line_with_keyword(f'slurm_file="{slurm_copy}"', 'slurm_file=', script_copy)
    
    #os.system(f'python3 {script_copy_name}')  # DEBUG
    os.system(f'sbatch {slurm_copy_name}')
    print(f'Sbatched {slurm_copy_name}...')

