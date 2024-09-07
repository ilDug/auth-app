import { InjectionToken } from '@angular/core';

// nome del token salvato nel localStorage
export const AUTH_TOKEN = new InjectionToken<string>('Auth JWT name');

// indirizzo del server di autenticazione
export const AUTH_SERVER = new InjectionToken<string>('Auth Server URL');