import io
import os

from typing import Iterator

def last_lines(filename: str, buffer_size: int = io.DEFAULT_BUFFER_SIZE) -> Iterator[str]:

    assert buffer_size > 0, 'buffer_size must be positive\n'

    with open(filename, 'rb') as file:
        file.seek(0, os.SEEK_END)
        cursor_position = file.tell()
        not_decoded_buffer = b''
        decoded_buffer = ''

        while cursor_position > 0:
            read_size = min(buffer_size, cursor_position)
            cursor_position -= read_size
            file.seek(cursor_position)

            text_block = file.read(read_size) + not_decoded_buffer
            not_decoded_buffer = b''

            # https://www.w3schools.com/charsets/ref_html_utf8.asp
            # cada caractere em utf-8 pode ter no maximo 4 bytes, por isso, caso cortemos um caractere no meio,
            # precisamos andar para a direita no maximo 4 bytes para conseguir decodificar o texto e armazenar os
            # caracteres nao decodificados em um buffer para concatenar com o bloco de texto seguinte
            for _ in range(4):
                if len(text_block) == 0:
                    continue
                try:
                    text_block = text_block.decode(encoding='utf-8')
                    break
                except:
                    not_decoded_buffer = not_decoded_buffer + text_block[:1]
                    text_block = text_block[1:]

            # caso nada tenha sido decodificado, guardamos os caracteres em um buffer e vamos para o proximo bloco de texto
            if len(text_block) == 0:
                continue

            # Para garantir que conseguimos ler uma linha inteira precisamos ler uma quebra de linha '\n'
            # ou chegar ao fim (inicio) do arquivo. Caso contrario, armazenamos o que ja foi decodificado
            # em outro buffer para concatenar com o proximo bloco de texto
            text_block = text_block + decoded_buffer
            if '\n' not in text_block and cursor_position > 0:
                decoded_buffer = text_block
                continue

            # Aqui splitamos o bloco de texto nas quebras de linha. Nao temos como garantir que o primeiro elemento
            # da lista é uma linha inteira, por isso vamos armazenar ele em um buffer para concatenar
            # com o proximo bloco e retornar os outros elementos da lista com a ordem invertida
            text_lines = text_block.splitlines(keepends=True)
            if cursor_position > 0:
                decoded_buffer = text_lines[0]
                text_lines = text_lines[1:]

            for line in reversed(text_lines):
                yield line

if __name__ == '__main__':
    lines = last_lines(filename='test_data/teste_problema_2.txt')
    for l in lines:
        print(l)