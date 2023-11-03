import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

# Globale Variable, um die Zensur-Mappings zu speichern
censor_map = {}
censor_index = 1

def edit_placeholder(original_word):
    # Ein Dialog, um den Platzhalter zu bearbeiten
    new_placeholder = simpledialog.askstring("Platzhalter bearbeiten", "Neuen Platzhalter eingeben:", initialvalue=censor_map[original_word])
    if new_placeholder:
        # Update the placeholder in the map and the table
        censor_map[original_word] = new_placeholder
        censor_table.item(original_word, values=(original_word, new_placeholder))

def add_word_to_censor():
    global censor_index
    try:
        # Versuche den ausgewählten Text zu bekommen
        selected_text = input_text.get(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        # Wenn kein Text ausgewählt ist, zeige das Popup zur Eingabe
        selected_text = simpledialog.askstring("Wort hinzufügen", "Welches Wort möchten Sie der Zensurliste hinzufügen?")

    if selected_text:
        placeholder = f"[CENSORED-{censor_index}]"
        censor_map[selected_text] = placeholder
        censor_index += 1
        censor_table.insert('', 'end', iid=selected_text, values=('', selected_text, placeholder))


def remove_selected_word():
    selected_item = censor_table.selection()
    if selected_item:
        original_word = censor_table.item(selected_item[0], 'values')[1]
        del censor_map[original_word]
        censor_table.delete(selected_item[0])

def censor_text():
    text_content = input_text.get("1.0", tk.END)
    for original, placeholder in censor_map.items():
        text_content = text_content.replace(original, placeholder)
    input_text.delete("1.0", tk.END)
    input_text.insert("1.0", text_content)

def on_double_click(event):
    # Finden Sie heraus, welche Zelle angeklickt wurde
    region = censor_table.identify('region', event.x, event.y)
    if region == "cell":
        # Starten Sie den Editor, wenn auf eine Zelle doppelgeklickt wird
        row_id = censor_table.identify_row(event.y)
        column = censor_table.identify_column(event.x)
        start_in_place_editing(row_id, column)

def start_in_place_editing(row_id, column):
    # Diese Funktion würde die In-Place-Bearbeitung starten
    pass  # Hier müsste die Logik zum Bearbeiten des Zelleninhalts implementiert werden

# Funktion, um alle Instanzen des gewählten Zensurworts im Text zu hervorzuheben
def highlight_text(event):
    # Löscht alle vorherigen Hervorhebungen
    input_text.tag_remove('highlight', '1.0', tk.END)
    
    # Was ist in der Liste ausgewählt
    try:
        selected_item = censor_table.focus()
        original_word = censor_table.item(selected_item, 'values')[1]
        start_index = '1.0'
        
        while True:
            # Findet das nächste Vorkommen des Originalworts
            start_index = input_text.search(original_word, start_index, stopindex=tk.END)
            if not start_index:
                break
            end_index = f"{start_index}+{len(original_word)}c"
            input_text.tag_add('highlight', start_index, end_index)
            # Bereite die Startposition für den nächsten Suchdurchgang vor
            start_index = end_index
        # Hervorhebungsfarbe festlegen
        input_text.tag_config('highlight', background='yellow')
    except IndexError:
        pass


# Hauptfenster erstellen
root = tk.Tk()
root.title("CensorGPT")

# Frame für die Tabelle und die Buttons
table_frame = tk.Frame(root)
table_frame.pack(side=tk.LEFT, fill=tk.Y)

# Tabelle für die zensierten Wörter
censor_table = ttk.Treeview(table_frame, columns=('Index', 'Original', 'Placeholder'))
censor_table.heading('#1', text='Index')
censor_table.heading('#2', text='Original')
censor_table.heading('#3', text='Placeholder')
censor_table.column('#1', width=0, stretch=tk.NO)  # Verstecke die 'Index' Spalte
censor_table['show'] = 'headings'  # Verstecke die erste leere Spalte
censor_table.pack()
censor_table.bind("<Double-1>", on_double_click)

# Button zum Hinzufügen zur Zensurliste
add_button = tk.Button(table_frame, text="Wort hinzufügen", command=add_word_to_censor)
add_button.pack()

# Button zum Entfernen aus der Zensurliste
remove_button = tk.Button(table_frame, text="Auswahl entfernen", command=remove_selected_word)
remove_button.pack()

# Button zum Bearbeiten des Platzhalters
edit_button = tk.Button(table_frame, text="Platzhalter bearbeiten", command=lambda: edit_placeholder(censor_table.item(censor_table.selection()[0], 'values')[1]))
edit_button.pack()

# Textfeld für den Eingabetext
input_text = tk.Text(root, height=20, width=50)
input_text.pack(side=tk.RIGHT)

# Schaltfläche zum Zensieren
censor_button = tk.Button(root, text="Zensieren", command=censor_text)
censor_button.pack(side=tk.BOTTOM)

# Hauptloop starten
root.mainloop()
