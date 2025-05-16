import os

os.environ['TCL_LIBRARY'] = r'C:\Users\jere0\AppData\Local\Programs\Python\Python313\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\jere0\AppData\Local\Programs\Python\Python313\tk\tk8.6'

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from fpdf import FPDF, XPos, YPos
from datetime import datetime
import random
import re
from PIL import Image


class PDF(FPDF):
    def multi_cell_custom(self, w, h, txt, border=0, align='C', fill=False):
        self.multi_cell(w, h, txt, border=border, align=align, fill=fill, new_x=XPos.RIGHT, new_y=YPos.TOP,
                        max_line_height=self.font_size)


def generar_factura():
    nombre_cliente = nombre_cliente_entry.get()
    apellidos_cliente = apellidos_cliente_entry.get()
    telefono_cliente = telefono_cliente_entry.get()
    dni_cliente = dni_cliente_entry.get()
    ciudad_cliente = ciudad_cliente_entry.get()
    productos_raw = nombre_servicio_entry.get()

    if not all([nombre_cliente, apellidos_cliente, telefono_cliente, dni_cliente, ciudad_cliente, productos_raw]):
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return

    productos = [p.strip() for p in productos_raw.split('-') if p.strip()]
    detalles_productos = []

    for producto in productos:
        cantidad = simpledialog.askstring("Cantidad", f"Ingrese la cantidad para '{producto}'")
        if cantidad is None:
            root.destroy()
            return
        garantia = simpledialog.askstring("Garantía", f"Ingrese la garantía (en meses) para '{producto}'")
        if garantia is None:
            root.destroy()
            return

        # Pedimos precio sin impuesto
        precio = simpledialog.askstring("Precio", f"Ingrese el precio (sin impuesto) para '{producto}'")
        if precio is None:
            root.destroy()
            return

        impuesto = simpledialog.askstring("Impuesto", f"Ingrese el impuesto en pesos para '{producto}'")
        if impuesto is None:
            root.destroy()
            return

        if not (cantidad and garantia and precio and impuesto):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        # Validaciones y formateo
        try:
            cantidad_int = int(cantidad)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return

        try:
            garantia_int = int(garantia)
            if garantia_int == 1:
                garantia_str = "1 mes"
            else:
                garantia_str = f"{garantia_int} meses"
        except ValueError:
            messagebox.showerror("Error", "La garantía debe ser un número entero.")
            return

        try:
            precio_float = float(precio)
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número.")
            return

        try:
            impuesto_float = float(impuesto)
            impuesto_str = f"${impuesto_float:.2f}"
        except ValueError:
            messagebox.showerror("Error", "El impuesto debe ser un número.")
            return

        total_float = precio_float + impuesto_float
        total_str = f"${total_float:.2f}"

        detalles_productos.append({
            "producto": producto,
            "cantidad": str(cantidad_int),
            "garantia": garantia_str,
            "impuesto": impuesto_str,
            "total": total_str
        })

    fecha_factura = datetime.now().strftime('%d/%m/%Y')
    identificador_factura = 'F' + str(random.randint(1000000, 9999999))

    pdf = PDF()
    pdf.add_page()

    logo_path = "sinfondo.png"
    try:
        Image.open(logo_path)
        pdf.image(logo_path, x=150, y=8, w=40)
    except Exception as e:
        print(f"No se pudo cargar el logo: {e}")

    pdf.set_xy(10, 10)
    pdf.set_font('helvetica', style='B', size=12)
    pdf.cell(0, 10, 'Areco Importaciones', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('helvetica', style='', size=12)
    pdf.cell(0, 10, 'Don Felix Vidarte, Las Piedras.', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, f'Fecha: {fecha_factura}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(20)
    pdf.set_font('helvetica', size=16, style='B')
    pdf.cell(0, 10, text='FACTURA DE COMPRA', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('helvetica', size=12)
    pdf.cell(0, 10, text=f'Número Factura: {identificador_factura}', align='C', border=1, new_x=XPos.LMARGIN,
             new_y=YPos.NEXT)
    pdf.ln(5)

    pdf.cell(0, 10, text='Datos del Cliente', align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('helvetica', style='B', size=10)
    pdf.cell(0, 10, text=f'Nombre: {nombre_cliente}', align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, text=f'Apellidos: {apellidos_cliente}', align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, text=f'Teléfono: {telefono_cliente}', align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, text=f'CI: {dni_cliente}', align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, text=f'Ciudad: {ciudad_cliente}', align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(5)
    pdf.cell(0, 10, text='Detalles del Servicio', align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Tabla
    pdf.set_fill_color(0, 0, 0)
    pdf.set_text_color(255, 255, 255)

    ancho_col = 190 / 5
    alto_fila = 10
    headers = ['Producto', 'Cantidad', 'Garantía', 'Impuesto', 'Total']

    for header in headers:
        pdf.multi_cell_custom(ancho_col, alto_fila, header, border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)

    for detalle in detalles_productos:
        pdf.multi_cell_custom(ancho_col, alto_fila, detalle["producto"], border=1, align='C')
        pdf.multi_cell_custom(ancho_col, alto_fila, detalle["cantidad"], border=1, align='C')
        pdf.multi_cell_custom(ancho_col, alto_fila, detalle["garantia"], border=1, align='C')
        pdf.multi_cell_custom(ancho_col, alto_fila, detalle["impuesto"], border=1, align='C')
        pdf.multi_cell_custom(ancho_col, alto_fila, detalle["total"], border=1, align='C')
        pdf.ln()

    pdf.ln(20)
    pdf.cell(0, 10, text='Gracias por su compra!', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    # Datos de contacto al final
    pdf.set_font('helvetica', size=10)
    pdf.cell(0, 5, text='(+598) 91 911 569', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, text='arecoimportaciones.uy@gmail.com', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Guardar archivo en la carpeta especificada
    output_folder = r"C:\Users\jere0\OneDrive\Desktop\Eccomerce\Boletas"
    os.makedirs(output_folder, exist_ok=True)

    safe_nombre = re.sub(r'[\\/*?:"<>|]', "", f'Factura_{nombre_cliente}_{apellidos_cliente}')
    pdf_file = os.path.join(output_folder, f'{safe_nombre}.pdf')

    try:
        pdf.output(pdf_file)
        messagebox.showinfo('Factura Generada', f'Se guardó en:\n{pdf_file}')
    except Exception as e:
        messagebox.showerror('Error', f'No se pudo guardar la factura:\n{e}')


# GUI
root = tk.Tk()
root.title('Facturas ArecoImportaciones')
root.geometry('300x370')

frame = ttk.Frame(root, padding='10')
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

etiquetas = ['Nombre', 'Apellidos', 'Teléfono', 'CI', 'Ciudad', 'Producto(s)']
entradas = []

for i, etiqueta in enumerate(etiquetas):
    ttk.Label(frame, text=etiqueta).grid(row=i, column=0, sticky=tk.W, padx=8, pady=8)
    entry = ttk.Entry(frame, width=30)
    entry.grid(row=i, column=1, sticky=(tk.W, tk.E))
    entradas.append(entry)

(nombre_cliente_entry, apellidos_cliente_entry, telefono_cliente_entry,
 dni_cliente_entry, ciudad_cliente_entry, nombre_servicio_entry) = entradas

style = ttk.Style()
style.configure("Custom.TButton", font=("Helvetica", 12, "bold"), foreground="white", background="#4CAF50", padding=10)
style.map("Custom.TButton", background=[("active", "#45a049"), ("!disabled", "#4CAF50")],
          foreground=[("disabled", "#aaa")])

generar_factura_btn = ttk.Button(frame, text='Generar Factura', command=generar_factura, style="Custom.TButton")
generar_factura_btn.grid(row=len(etiquetas), column=0, columnspan=2, pady=10)

root.mainloop()
