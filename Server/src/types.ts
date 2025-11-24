export type RegisterPerfil = {
  nombre: string;
  apellidos: string;
  telefono: string;
  fecha_nacimiento: string;
  pais: string;
  hobbie: string;
  color_preferido?: string;  
  tema_preferido?: string;   
  cancion_preferida?: string; 
  color_preferido?: string;  
  tema_preferido?: string;   
  cancion_preferida?: string; 
};

export type RegisterCuenta = {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
};

export type RegisterPago = {
  titular: string;
  numero_tarjeta: string;
  expiracion: string;
};

export type RegisterReq = {
  perfil: RegisterPerfil;
  cuenta: RegisterCuenta;
  pago: RegisterPago;
  acepto_tyc: boolean;
  avatar_b64?: string; // imagen en base64 desde el cliente
  avatar_mime?: string; // ej. "image/png"
  avatar_b64?: string; // imagen en base64 desde el cliente
  avatar_mime?: string; // ej. "image/png"
};

export type UserRecord = {
  id: string;
  username: string;
  email: string;
  password_hash: string;
  perfil: RegisterPerfil;
  pago: RegisterPago;
  acepto_tyc: boolean;
  createdAt: string;
  updatedAt: string;
  resetTokenHash?: string;
  resetExpires?: number;
  avatar?: null | {
    path: string;   // ruta a archivo cifrado (JSON con nonce/ct)
    mime: string;
  };
  primera_vez?: boolean;
};

export type DBShape = { usuarios: UserRecord[] };
