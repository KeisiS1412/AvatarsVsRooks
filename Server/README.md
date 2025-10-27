Servidor local en Node.js + TypeScript para manejar el registro, login y almacenamiento cifrado de usuarios del juego AvatarsVsRooks. Los datos se guardan en un archivo cifrado (usuarios.json.enc) usando XChaCha20-Poly1305 y las contraseñas se protegen con Argon2. Permite ejecutar el juego localmente, con o sin conexión, y compartir la misma base cifrada entre varios desarrolladores.

Para instalarlo, asegúrate de tener Node.js 20 o superior y npm. Luego abre una terminal en la carpeta Server y ejecuta:  
npm install  
Después crea el archivo .env (si no existe) con:  
cp .env.example .env  
Abre el archivo .env y asegúrate de que tenga lo siguiente:  
PORT=3007  
KEY_B64=  
DATA_FILE=./usuarios.json.enc  
PORT define el puerto del servidor (por defecto 3007), KEY_B64 es la clave secreta en Base64 (todos los desarrolladores deben usar la misma), y DATA_FILE es el archivo cifrado donde se guardan los usuarios. Si dejas KEY_B64 vacío, el servidor generará automáticamente una nueva clave y un archivo secret.key.

Para ejecutar el servidor, corre el comando:  
npm run dev  
Si todo funciona, aparecerá “Servidor corriendo en http://localhost:3007”. Puedes probarlo abriendo esa dirección en el navegador o ejecutando curl http://localhost:3007/health y verás {"ok":true} si está activo.

El servidor tiene tres rutas:  
GET /health (verifica que el servidor funciona),  
POST /auth/register (registra un nuevo usuario) y  
POST /auth/login (verifica usuario y contraseña).  

Ejemplo de login en PowerShell:  
$login = @{ username_or_email = "fabian"; password = "ABC12345" } | ConvertTo-Json  
Invoke-RestMethod -Method POST "http://localhost:3007/auth/login" -ContentType "application/json" -Body $login  

Archivos importantes:  
.env contiene las variables de entorno y no debe subirse al rimepositorio.  
secret.key es la clave generada localmente y tampoco debe subirse.  
usuarios.json.enc es la base de datos cifrada, puede compartirse solo si el repositorio es privado y todos usan la misma clave.  

Para que todos los desarrolladores usen el mismo archivo cifrado, uno de ellos debe abrir Server/secret.key, copiar el contenido completo (una línea en Base64) y pegarlo en la variable KEY_B64 del .env de todos los demás. Todos deben tener también el archivo usuarios.json.enc en la carpeta Server.  

El archivo .gitignore debe contener lo siguiente:  
node_modules/  
dist/  
.env  
secret.key  
usuarios.json.enc  

Después de clonar el proyecto, cualquier desarrollador puede ejecutar:  
cd Server  
npm install  
cp .env.example .env  
(pegar la misma KEY_B64 compartida)  
npm run dev  

El servidor se ejecutará en http://localhost:3007 y leerá los mismos datos cifrados para todos.  
