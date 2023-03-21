from pyodide import create_proxy
import asyncio
import io
from PIL import Image

async def upload(e):
    file_list = e.target.files
    first=file_list.item(0)
    array_buf = Uint8Array.new(await first_.arrayBuffer())
    bytes_list = bytearray(array_buf)
    my_bytes=io.BytesIO(bytes_list)
    img=Image.open(my_bytes)
