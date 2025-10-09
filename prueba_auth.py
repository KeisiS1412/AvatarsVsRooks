from auth import register_user, verify_login, get_profile

u = "fabian_demo2"
uid = register_user(u, "S3guro#2025", "Fabián Sanchez", "fabian@correo.com", "8888-8888")
print("creado:", uid)

print("login:", verify_login(u, "S3guro#2025"))
print("perfil:", get_profile(u))
