from database import Child, session
from datetime import date

def add_new_child(session):
    new_child = Child(
        first_name=input("Podaj imię dziecka: "),
        last_name=input("Podaj nazwisko dziecka: "),
        birth_date=date(int(input("Podaj rok urodzenia dziecka: ")), int(input("Podaj miesiąc urodzenia dziecka: ")), int(input("Podaj dzień urodzenia dziecka: "))),   
        gender=input("Podaj płeć dziecka (M/K): "),
        notes=input("Podaj notatki o dziecku: ")
    )
    session.add(new_child)
    session.commit()
    print("Dziecko zostało dodane do bazy.")

def print_all_children(session):
    children = session.query(Child).all()  
    if not children:
        print("Brak dzieci w bazie.")
        return

    print("Lista dzieci w bazie:")
    for child in children:
        print(f"ID: {child.id} - {child.first_name} {child.last_name}")

def delete_child_by_id(session, child_id):
    # 1. Znajdź dziecko w bazie
    child = session.query(Child).filter_by(id=child_id).first()
    
    if not child:
        print(f"Nie znaleziono dziecka o ID {child_id}.")
        return
    
    # 2. Usuń wszystkie badania i odpowiedzi powiązane z dzieckiem
    for exam in child.examinations:
        for answer in exam.answers:
            session.delete(answer)  # usuwa odpowiedzi
        session.delete(exam)        # usuwa badanie
    
    # 3. Usuń samo dziecko
    session.delete(child)
    
    # 4. Zatwierdź zmiany w bazie
    session.commit()
    
    print(f"Dziecko o ID {child_id} i wszystkie jego dane zostały usunięte.")

while True:
    print("wybierz opcję:")
    print("1. Dodaj nowe dziecko")
    print("2. Pokaż wszystkie dzieci")
    print("3. Usuń dziecko po ID")
    choice = input("Wybór: ")   
    if choice == "1":
     add_new_child(session)  
    elif choice == "2":
        print_all_children(session) 
    elif choice == "3":
        delete_child_by_id(session, int(input("Podaj ID dziecka do usunięcia: ")))
    else:
        print("Nieprawidłowy wybór!")
        print("Nieznana opcja.")    
