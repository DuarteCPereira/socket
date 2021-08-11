import socket
import select
import errno
import sys
import time
import pickle



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


    test_client_func(username, HEADER_LENGTH, IP, PORT)

if __name__ == "__main__":
    main()