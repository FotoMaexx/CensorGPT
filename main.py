import tkinter as tk
from tkinter import ttk, simpledialog

# Globale Variable, um die Zensur-Mappings zu speichern
censor_map = {}
censor_index = 1

# Funktion zum Hinzufügen eines Worts zur Zensurliste
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
        censor_table.insert('', 'end', iid=selected_text, values=(selected_text, placeholder))

# Funktion zum Entfernen eines Worts aus der Zensurliste
def remove_selected_word():
    selected_item = censor_table.selection()
    if selected_item:
        original_word = censor_table.item(selected_item[0], 'values')[0]
        del censor_map[original_word]
        censor_table.delete(selected_item[0])

# Funktion zum Zensieren des Textes
def censor_text():
    text_content = input_text.get("1.0", tk.END)
    for original, placeholder in censor_map.items():
        text_content = text_content.replace(original, placeholder)
    input_text.delete("1.0", tk.END)
    input_text.insert("1.0", text_content)

# Funktion zum Hervorheben aller Instanzen des ausgewählten Texts
def highlight_all_instances(event=None):
    # Entferne alle vorherigen Highlights
    input_text.tag_remove('highlight', '1.0', tk.END)

    # Ermittle den ausgewählten Text und prüfe, ob er nicht leer ist
    try:
        selection = input_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        if selection.strip() == '':  # Ignoriere, wenn nur Leerzeichen ausgewählt sind
            return
    except tk.TclError:
        return  # Kein Text ist ausgewählt

    # Suche und hebe alle Instanzen des ausgewählten Texts hervor
    start_idx = '1.0'
    while True:
        start_idx = input_text.search(selection, start_idx, nocase=True, stopindex=tk.END)
        if not start_idx:
            break
        end_idx = f"{start_idx}+{len(selection)}c"
        input_text.tag_add('highlight', start_idx, end_idx)
        start_idx = end_idx
    # Konfiguriere das Highlight-Tag, um die Hintergrundfarbe zu ändern
    input_text.tag_config('highlight', background='yellow')

# Diese Funktion sorgt dafür, dass das Highlighting sofort aktiviert wird, wenn die Anwendung startet
def init_highlighting(event=None):
    input_text.tag_configure('highlight', background='yellow')
    input_text.bind('<<Selection>>', highlight_all_instances)

# Hauptfenster erstellen
root = tk.Tk()
root.title("CensorGPT")

# Frame für die Tabelle und die Buttons
table_frame = tk.Frame(root)
table_frame.pack(side=tk.LEFT, fill=tk.Y)

# Tabelle für die zensierten Wörter
censor_table = ttk.Treeview(table_frame, columns=('Original', 'Placeholder'))
censor_table.heading('#1', text='Original')
censor_table.heading('#2', text='Placeholder')
censor_table['show'] = 'headings'  # Verstecke die erste leere Spalte
censor_table.pack()

# Button zum Hinzufügen zur Zensurliste
add_button = tk.Button(table_frame, text="Wort hinzufügen", command=add_word_to_censor)
add_button.pack()

# Button zum Entfernen aus der Zensurliste
remove_button = tk.Button(table_frame, text="Auswahl entfernen", command=remove_selected_word)
remove_button.pack()

# Textfeld für den Eingabetext
input_text = tk.Text(root, height=20, width=50)
input_text.pack(side=tk.RIGHT)

# Bindet das Highlighting an das Ereignis, dass Text im Textfeld ausgewählt wird
input_text.bind('<<Selection>>', highlight_all_instances)


# Schaltfläche zum Zensieren
censor_button = tk.Button(root, text="Zensieren", command=censor_text)
censor_button.pack(side=tk.BOTTOM)

# In-Place-Editing für die Tabelle
def edit_cell(event):
    # Welche Zelle wurde ausgewählt
    column = censor_table.identify_column(event.x)
    row_id = censor_table.identify_row(event.y)
    entry_popup(event.x_root, event.y_root, column, row_id)

# Popup-Entry für die direkte Bearbeitung
def entry_popup(x, y, column, row_id):
    # Schließe den vorherigen Popup, falls vorhanden
    if hasattr(entry_popup, 'entry'):
        entry_popup.entry.destroy()
    # Erstelle ein neues Entry-Widget
    entry_popup.entry = tk.Entry(root)
    entry_popup.entry.place(x=x, y=y)
    
    # Hier holen wir den Index der Spalte basierend auf dem Namen der Spalte
    col_index = censor_table["displaycolumns"].index(column[1:])
    original_value = censor_table.item(row_id, 'values')[col_index]
    entry_popup.entry.insert(0, original_value)
    entry_popup.entry.select_range(0, tk.END)
    entry_popup.entry.focus()
    
    def on_entry_validate():
        # Update Table and Map
        new_value = entry_popup.entry.get()
        if column == "#1":
            # Update des Originalworts und dessen Platzhalters
            old_word = original_value
            new_word = new_value
            new_placeholder = censor_map[old_word]
            censor_map[new_word] = new_placeholder
            del censor_map[old_word]
            censor_table.item(row_id, values=(new_word, new_placeholder))
        elif column == "#2":
            # Update nur des Platzhalters
            original_word = censor_table.item(row_id, 'values')[0]
            censor_map[original_word] = new_value
            censor_table.item(row_id, values=(original_word, new_value))
        entry_popup.entry.destroy()
    
    entry_popup.entry.bind('<Return>', lambda e: on_entry_validate())
    entry_popup.entry.bind('<Escape>', lambda e: entry_popup.entry.destroy())

censor_table.bind('<Double-1>', edit_cell)

# Funktion zum Hervorheben des ausgewählten Worts im Textfeld
def highlight_word_in_text(word):
    input_text.tag_remove('highlight', '1.0', tk.END)
    if word:
        idx = '1.0'
        while idx:
            idx = input_text.search(word, idx, nocase=True, stopindex=tk.END)
            if idx:
                lastidx = '%s+%dc' % (idx, len(word))
                input_text.tag_add('highlight', idx, lastidx)
                idx = lastidx
        input_text.tag_config('highlight', background='yellow')

# Funktion, die aufgerufen wird, wenn ein Eintrag in der Tabelle ausgewählt wird
def on_select(event):
    selected = censor_table.focus()
    if selected:
        word = censor_table.item(selected, 'values')[0]
        highlight_word_in_text(word)

censor_table.bind('<<TreeviewSelect>>', on_select)

# Hauptloop starten
root.mainloop()
