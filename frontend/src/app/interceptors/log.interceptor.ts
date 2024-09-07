import { HttpErrorResponse, HttpHandlerFn, HttpInterceptorFn, HttpRequest, HttpResponse } from '@angular/common/http';
import { catchError, tap, throwError } from 'rxjs';

export const logInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn) => {
    
    const started = Date.now();

    return next(req)
        .pipe(
            tap(event => {
                const ok = event instanceof HttpResponse ? 'succeeded' : 'failed'
                const elapsed = Date.now() - started;
                const msg = `--DAG-- ${req.method} "${req.urlWithParams}" ${ok} in ${elapsed} ms.`;
                if (event instanceof HttpResponse) console.log(msg, event);
            }),
            catchError((error: HttpErrorResponse) => {
                console.log(error)
                return throwError(() => error)
            })
        )
};
