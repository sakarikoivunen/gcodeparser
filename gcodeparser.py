import sys
from datetime import datetime

# Change the following based on your case
RX=178
RY=0
RZ=5

EXPORT_NAME="0GCODE"
TOOL=0
FRAME=9
SPEED_PROCESS=3.8

def xyz_to_position(x, y, z, i_pos):
    return f"C{i_pos:05d}={x:.3f},{y:.3f},{z:.3f},{RX:.4f},{RY:.4f},{RZ:.4f}"

def generate_bc(i_pos):
    # Change base axis (gantry) positions if needed
    return f"BC{i_pos:05d}=5614,8503,60"

def parse_gcode(gcode):
    program_instructions=[]
    first=True
    position_data=[]
    lines = gcode.splitlines()
    z_last = 0.0
    arc_on = False

    for i, line in enumerate(lines):
        if line.startswith(";LAYER"):
            program_instructions.append(f"'*** {line[1:]} ***")
        if line.startswith("G0") or line.startswith("G1"):
            parts = line.split()
            x, y, z, e = None, None, None, None
            i_pos=len(position_data)

            for part in parts:
                if part.startswith("X"):
                    x = float(part[1:])
                elif part.startswith("Y"):
                    y = float(part[1:])
                elif part.startswith("Z"):
                    z = float(part[1:])
                elif part.startswith("E"):
                    e = float(part[1:])

            if z is None:
                z = z_last
            else:
                z_last = z

            if not arc_on and e is not None:
                program_instructions.append("CALL JOB:ARCON")
                arc_on = True

            if arc_on and e is None:
                program_instructions.append("CALL JOB:ARCOFF")
                arc_on = False

            if x is not None or y is not None:
                if first:
                    first=False
                    position_data.append(xyz_to_position(x,y,z+100,i_pos))
                    program_instructions.append(f"MOVJ C{i_pos:05d} BC{i_pos:05d} VJ=10.00")
                    i_pos+=1
                position_data.append(xyz_to_position(x,y,z,i_pos))
                program_instructions.append(f"MOVL C{i_pos:05d} BC{i_pos:05d} V={SPEED_PROCESS:.1f}")
    return(position_data, program_instructions)

def main():
    if len(sys.argv) < 2:
        print("Usage: python gcodeparser.py <g-code-file>")
        sys.exit(1)

    gcode_file = sys.argv[1]

    try:
        with open(gcode_file, 'r') as file:
            gcode_content = file.read()

        position_data, program_instructions = parse_gcode(gcode_content)

    except FileNotFoundError:
        print(f"File '{gcode_file}' was not found.")
        sys.exit(1)

    now = datetime.now()
    formatted_date_time = now.strftime("%Y/%m/%d %H:%M")

    code = []

    code.append("/JOB")
    code.append(f"//NAME {EXPORT_NAME}")
    code.append("//POS")
    code.append(f"///NPOS {len(position_data)},{len(position_data)},0,0,0,0")
    code.append(f"///TOOL {TOOL}")
    code.append("///POSTYPE PULSE")
    code.append("///PULSE")

    for i in range(len(position_data)):
        code.append(generate_bc(i))

    code.append(f"///USER {FRAME}")
    code.append("///POSTYPE USER")
    code.append("///RECTAN")
    code.append("///RCONF 0,0,0,0,0,0,0,0")

    code.extend(position_data)

    code.append("//INST")
    code.append(f"///DATE {formatted_date_time}")
    code.append("///ATTR SC,RW,RJ")
    code.append("///GROUP1 RB1,BS1")
    code.append("NOP")
    code.extend(program_instructions)
    code.append("END")

    file_name_jbi = f"{EXPORT_NAME}.JBI"

    with open(file_name_jbi, 'w') as file:
        for line in code:
            file.write(f"{line}\n")

    print(f"File '{file_name_jbi}' was created.")

if __name__ == "__main__":
    main()