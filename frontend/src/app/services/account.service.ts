import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { AuthService } from './auth.service';
import { catchError, finalize, map, Observable, of, tap } from 'rxjs';
import { Md5 } from 'ts-md5';


/**
 * risposta del login
 */
export type LoginResponse = {
    /** dag access token */
    dat: string,

    /** dag refresh token */
    drt: string

    /** fingerprint */
    dfp: string
}



/**
 * Service for handling user account operations.
 */
@Injectable({
    providedIn: 'root'
})
export class AccountService {
    #http = inject(HttpClient);
    #auth = inject(AuthService);


    PENDING = signal<boolean>(false);


    /**
     * Logs in a user with the provided email and password.
     * @param email - The user's email.
     * @param password - The user's password.
     * @returns An Observable that emits a boolean indicating whether the login was successful.
     */
    login(email: string, password: string): Observable<boolean> {
        this.PENDING.set(true);
        return this.#http.post<LoginResponse>(`/api/v1/account/login`, { email, password })
            .pipe(
                map(res => res.dat),
                tap(jwt => this.#auth.jwt.set(jwt as string)),
                map(jwt => !!jwt),
                finalize(() => this.PENDING.set(false))
            )
    }


    /**
     * Registers a new user account.
     * 
     * @param email - The email address of the user.
     * @param password - The password for the user account.
     * @returns An Observable that emits a boolean indicating the success of the registration.
     */
    register(email: string, password: string): Observable<boolean> {
        this.PENDING.set(true);
        return this.#http.post<LoginResponse>(`/api/v1/account/register`, { email, password }, { withCredentials: true })
            .pipe(
                map(res => res.dat),
                tap(jwt => this.#auth.jwt.set(jwt as string)),
                map(jwt => !!jwt),
                finalize(() => this.PENDING.set(false))
            )
    }




    /**
     * Resends the activation email for the specified email address.
     * 
     * @param email - The email address to resend the activation email to.
     * @returns An Observable that emits a boolean indicating whether the activation email was successfully resent.
     */
    resendActivation(email: string): Observable<boolean> {
        this.PENDING.set(true);
        const hash = Md5.hashStr(email)
        return this.#http.get<boolean>(`/api/v1/account/resend-activation/${hash}`)
            .pipe(
                finalize(() => this.PENDING.set(false))
            )
    }


    /**
     * Activates a user account using the provided activation key.
     * 
     * @param activationKey - The activation key for the account, providec by email.
     * @returns An Observable that emits a boolean indicating whether the activation was successful.
     */
    activate(activationKey: string): Observable<{ success: boolean, message: string }> {
        this.PENDING.set(true);
        return this.#http.get<any>(`/api/v1/account/activate/${activationKey}`, { observe: 'response' })
            .pipe(
                map(res => ({ success: res.status === 200, message: res.body as string })),
                finalize(() => this.PENDING.set(false))
            )
    }


    /**
     * Checks if an account with the specified email address exists.
     * 
     * @param email - The email address to check for.
     * @returns An Observable that emits a boolean indicating whether an account with the specified email address exists
     */
    emailExists(email: string): Observable<boolean> {
        const hash = Md5.hashStr(email)
        return this.#http.get<boolean>(`/api/v1/account/exists/${hash}`)
    }



    /**
     * Sends a request to recover the password associated with the provided email.
     * the user will get an email with a link to reset the password
     * 
     * @param email - The email address associated with the account.
     * @returns An Observable that emits a boolean indicating the success of the password recovery request.
     */
    recoverPassword(email: string): Observable<boolean> {
        this.PENDING.set(true);
        return this.#http.post<boolean>(`/api/v1/account/password/recover`, { email: email })
            .pipe(
                finalize(() => this.PENDING.set(false))
            )
    }



    /**
     * Intializes all checks for the password reset process, using the provided reset key.
     * 
     * @param restoreKey - The restore key used to restore the password.
     * @returns An observable that emits a string representing the user UID.
     */
    restoreInit(restoreKey: string): Observable<string> {
        this.PENDING.set(true);
        return this.#http.get<string>(`/api/v1/account/password/restore/init/${restoreKey}`)
            .pipe(
                finalize(() => this.PENDING.set(false))
            )
    }



    /**
     * Restores the password using the provided restore key and new password.
     * @param restoreKey - The restore key used to verify the password restoration.
     * @param newPassword - The new password to set.
     * @returns An Observable that emits a boolean indicating whether the password restoration was successful.
     */
    restoreSet(restoreKey: string, newPassword: string): Observable<boolean> {
        this.PENDING.set(true);
        return this.#http.post<boolean>(`/api/v1/account/password/restore/set`, { key: restoreKey, newpassword: newPassword })
            .pipe(
                finalize(() => this.PENDING.set(false))
            )
    }



}
