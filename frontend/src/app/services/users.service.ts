import { HttpClient } from '@angular/common/http';
import { inject, Injectable, signal } from '@angular/core';
import { AUTH_SERVER } from '../injection-tokens';
import { catchError, finalize, from, lastValueFrom, map, of, switchMap, tap } from 'rxjs';
import { User } from '../classes/user';

@Injectable({
    providedIn: 'root'
})
export class UsersService {

    constructor() {
        this.load();
    }

    #http = inject(HttpClient);

    private serverUrl = inject(AUTH_SERVER);

    collection = signal<User[]>([]);

    PENDING = signal<boolean>(false);

    request$ = of(true)
        .pipe(
            tap(_ => this.PENDING.set(_)),
            switchMap(() => this.#http.get(`${this.serverUrl}/users`)),
            catchError(err => of([])),
            map((users: any[]) => users.map(u => new User(u))),
            tap(users => this.collection.set(users)),
            finalize(() => this.PENDING.set(false))
        )

    public load = (): Promise<User[]> => lastValueFrom(this.request$);


}
