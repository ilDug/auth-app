import { HttpErrorResponse, HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { NgxToastService } from '@ildug/ngx-toast';
import { catchError, throwError } from 'rxjs';

export const xErrorsInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn) => {
    const toast = inject(NgxToastService);

    return next(req)
        .pipe(
            catchError((error: HttpErrorResponse) => {

                const xError = error.headers.has("X-Error")
                    ? error.headers.get("X-Error")
                    : error.error.error || error.error.message || error.message || error.statusText

                toast.error(xError, 5000);
                return throwError(() => xError);
            })
        )
};
