from printers import Printer
from modules import Head
import socket
import select
import errno
import sys
import time
import pickle


def send_message(string):
    h2.add_instruction_to_queue(string+"\n")
    h2.send_next_instruction(show=True)
    h2.read_serial_message(show=True)
    return None


def test_client_func(username, HEADER_LENGTH, IP, PORT):
    #my_username = input("Username: ")
    my_username = username
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)

    username = my_username.encode("utf-8")
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
    client_socket.send(username_header + username)


    a = True
    b = True
    c = True
    while b:
        print(f"Choose a calibration option:")
        print(f"1 - Measure distance.")
        print(f"2 - Calibrate E-steps on xx direction.")
        process = input(f"{my_username} > ")

        #Processar as ações necessárias para cada processo

        #Medir distância
        if process == "1":
            message = f"Proc1"
            message = message.encode("utf-8")
            message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(message_header+message)
            #Esperar 5 segundos para o RP receber a ordem de começar a gravar e mandar a máquina mover
            time.sleep(5)
            send_message("G10 F100")

            while a:
                try:
                    while a:
                        #receive things
                        username_header = client_socket.recv(HEADER_LENGTH)
                        if not len(username_header):
                            print("connection closed by the server")
                            sys.exit()

                        username_length = int(username_header.decode("utf-8").strip())
                        username = client_socket.recv(username_length).decode("utf-8")

                        message_header = client_socket.recv(HEADER_LENGTH)
                        message_length = int(message_header.decode("utf-8").strip())
                        #message = client_socket.recv(message_length).decode("utf-8")
                        message = client_socket.recv(message_length)

                        d = pickle.loads(message)
                        print(f"{username} > {d}")
                        print(f"O vector recebido foi: {d} ")
                        if message_length > 0:
                            a = False

                except IOError as e:
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        print('Reading error', str(e))
                        sys.exit()
                    continue
                
                except Exception as e:
                    print('General error', str(e))
                    sys.exit()
                    pass
        
        #Calibrar E-Steps
        if process == "2":
            #beforing calling this function, M503 and M83 must be sent to printer
            #Get A parameter from M503

            while c:
                a = True
                message = f"Proc2"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header+message)
                time.sleep(1)

                #Send A to RP
                A = 10
                message = f"{A}"
                message = message.encode("utf-8")
                message_header = f"{len(message) :< {HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header + message)

                #Esperar 5 segundos para o RP receber a ordem de começar a gravar e mandar a máquina mover
                time.sleep(5)
                '''Substituir por comando de mover'''


                while a:
                    try:
                        while a:
                            #receive things
                            username_header = client_socket.recv(HEADER_LENGTH)
                            if not len(username_header):
                                print("connection closed by the server")
                                sys.exit()

                            username_length = int(username_header.decode("utf-8").strip())
                            username = client_socket.recv(username_length).decode("utf-8")

                            message_header = client_socket.recv(HEADER_LENGTH)
                            message_length = int(message_header.decode("utf-8").strip())
                            message = client_socket.recv(message_length).decode("utf-8")
                            D = float(message)
                            

                            if abs(D - A) < 0.5:
                                c = False
                                a = False
                                print(D)
                                break
                            elif abs(D - A) > 0.5:
                                print("Parametro nao esta afinado")
                                a = False

                            

                    except IOError as e:
                        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                            print('Reading error', str(e))
                            sys.exit()
                        continue
                    
                    except Exception as e:
                        print('General error', str(e))
                        sys.exit()
                        pass
    return None

def main():
    username = "PC"
    HEADER_LENGTH = 10
    IP = "127.0.0.1"
    PORT = 1234

    printer = Printer.create_printer_standard_from_parts_dimensions(length_x=380, length_y=400, length_z=50)
    configuration = [2]
    for pos_y in range(len(configuration)):
        for pos_x in range(configuration[pos_y]):
            aux_head = Head.create_standard_head()
            aux_head.set_position_in_rails(pos_x=pos_x, pos_y=pos_y)
            aux_head.calculate_origin_point(nr_rails=len(configuration), nr_heads_in_rail=configuration[pos_y])
            aux_head.place_head_in_point(point=aux_head.reference_point)
            aux_head.calculate_max_x_reference_point(nr_heads_in_rail=configuration[pos_y], length_x=printer.length_x)
            aux_head.calculate_safe_range(nr_rails=len(configuration))
            aux_head.calculate_soft_limits_from_reference_points()
            aux_head.create_safe_area(nr_rails=len(configuration))
            aux_head.create_unsafe_area(nr_rails=len(configuration))

            printer.add_head_to_printer(aux_head)

    printer.set_heads_position_on_rails()
    printer.update_printer_dimensions()
    printer.place_heads_in_home_point()
    printer.calculate_rails_build_area()
    printer.calculate_neighbours_heads()

    printer.set_com_ports(["COM3", "COM4"])
    #printer.list_of_heads[0].material_id = 0
    #printer.list_of_heads[1].material_id = 1

    h1 = printer.list_of_heads[0]
    h2 = printer.list_of_heads[1]


    h1.connect_to_serial(h1.serial_port)
    h2.connect_to_serial(h2.serial_port)

    h2.flush_start_messages()
    message = h2.read_serial_message(show=False)


    test_client_func(username, HEADER_LENGTH, IP, PORT)

if __name__ == "__main__":
    main()