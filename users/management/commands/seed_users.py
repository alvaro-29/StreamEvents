# users/management/commands/seed_users.py

# Importem la classe base per crear comandes personalitzades de Django
# Importem el model d'usuari actual (pot ser User o un model personalitzat)
from django.contrib.auth import get_user_model
# Importem el model de grups
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
# Importem el suport per fer transaccions a la base de dades
from django.db import transaction

# Assignem el model d'usuari a la variable User
User = get_user_model()


# Creem la comanda personalitzada
class Command(BaseCommand):
    # Missatge que apareix quan fem `python manage.py help seed_users`
    help = "🌱 Crea usuaris de prova per al desenvolupament"

    # Definim els arguments que pot rebre la comanda
    def add_arguments(self, parser):
        # Argument --users per indicar el nombre d'usuaris a crear (per defecte 10)
        parser.add_argument(
            "--users",
            type=int,
            default=10,
            help="Nombre d'usuaris a crear (per defecte 10)",
        )
        # Argument --clear per eliminar tots els usuaris existents abans de crear-ne de nous
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Elimina tots els usuaris existents abans de crear-ne de nous",
        )

    # Funció principal que s'executa quan cridem la comanda
    def handle(self, *args, **options):
        num_users = options["users"]  # Nombre d'usuaris a crear
        clear = options["clear"]  # Saber si hem d'esborrar els usuaris existents

        # Si l'usuari ha passat --clear, eliminem els usuaris existents (excepte superusuaris)
        if clear:
            self.stdout.write("🗑️  Eliminant usuaris existents...")
            count = 0
            for user in User.objects.all():
                if not user.is_superuser:
                    user.delete()
                    count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Eliminats {count} usuaris"))

        # Executem la creació dins d'una transacció per assegurar la coherència
        with transaction.atomic():
            groups = self.create_groups()  # Creem els grups necessaris
            users_created = self.create_users(num_users, groups)  # Creem els usuaris

        # Missatge final indicant quants usuaris s'han creat
        self.stdout.write(
            self.style.SUCCESS(f"✅ {users_created} usuaris creats correctament!")
        )

    # Funció per crear els grups necessaris
    def create_groups(self):
        """Crea els grups necessaris"""
        group_names = ["Organitzadors", "Participants", "Moderadors"]  # Llista de grups
        groups = {}

        for name in group_names:
            # get_or_create crea el grup si no existeix, sinó retorna l'existent
            group, created = Group.objects.get_or_create(name=name)
            groups[name] = group
            if created:
                self.stdout.write(f'  ✓ Grup "{name}" creat')

        return groups

    # Funció per crear els usuaris de prova
    def create_users(self, num_users, groups):
        """Crea usuaris de prova"""
        users_created = 0

        # Creem un superusuari admin si no existeix
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@streamevents.com",
                "first_name": "Admin",
                "last_name": "Sistema",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin123")  # Assignem contrasenya
            admin.save()
            self.stdout.write("  ✓ Superusuari admin creat")
            users_created += 1

        # Creem els usuaris normals
        for i in range(1, num_users + 1):
            username = f"user{i:03d}"  # Generem un username tipus user001, user002...

            # Assignem grup segons el número d'usuari
            if i % 3 == 0:
                group = groups["Organitzadors"]
                role = "org"
            elif i % 2 == 0:
                group = groups["Moderadors"]
                role = "mod"
            else:
                group = groups["Participants"]
                role = "part"

            # get_or_create assegura que no dupliquem usuaris
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@streamevents.com",
                    "first_name": f"Nom{i}",
                    "last_name": f"Cognom{i}",
                    "is_active": True,
                },
            )

            if created:
                user.set_password("password123")  # Assignem contrasenya per defecte
                user.save()
                user.groups.add(group)  # Afegim l'usuari al grup corresponent
                users_created += 1
                self.stdout.write(f"  ✓ Usuari {username} ({role}) creat")

        return users_created
