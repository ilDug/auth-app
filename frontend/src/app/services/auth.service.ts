import { computed, effect, inject, Injectable, signal } from '@angular/core';
import { AUTH_TOKEN } from '../injection-tokens';
import { HttpClient } from '@angular/common/http';
import { JWT } from '../classes/jwt';
import { NgxToastService } from '@ildug/ngx-toast';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private readonly tokenName: string = inject(AUTH_TOKEN);

    #toast = inject(NgxToastService);

    // JWT  - the raw token string
    public jwt = signal<string>(localStorage.getItem(this.tokenName) ?? null);

    // JWT  - the decoded token
    public token = computed(() => {
        if (!this.jwt()) return null;

        try {
            return new JWT(this.jwt());
        } catch (e) {
            this.#toast.error('Errore nella decodifica del token', 5000);
            return null;
        }
    });

    // user id
    public uid = computed<string>(() => this.token()?.claims["uid"] ?? null);

    // token identifier
    public jti = computed<string>(() => this.token()?.claims["jti"] ?? null);

    // user email
    public email = computed<string>(() => this.token()?.claims["email"] ?? null);

    // user username
    public username = computed<string>(() => this.token()?.claims["username"] ?? null);


    /** salva il jwt nel localStorage ogni volta che viene aggiornato */
    #storeTokenEffect = effect(() => {
        // se è annullato lo rimuove dal localStorage
        if (this.jwt() === null)
            localStorage.removeItem(this.tokenName);
        // altrimenti salva le modifiche
        else
            localStorage.setItem(this.tokenName, this.jwt());
    })

    /** verifica se l'utente è autenticato tramite JWT */
    public authenticated = computed<boolean>(() => {
        try {
            return this.token() !== null && !this.token().expired;
        } catch (e) {
            return false;
        }
    })


    /** verifica se l'utente posside le autorizzazioni */
    public authorized(permissions: string | string[]): boolean {
        permissions = Array.isArray(permissions) ? permissions : [permissions];
        if (!this.authenticated()) return false;
        return permissions.every(p => this.token().claims['authorizations'].includes(p));
    }


    /** effettua il logout */
    logout() {
        this.jwt.set(null);
    }


}
