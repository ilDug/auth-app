import { HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn) => {
    // // inject the service
    // const auth = inject(AuthService);

    // // Get the auth token from the service.
    // const authToken = "Bearer " + auth.jwt();

    // // Clone the request and replace the original headers with
    // // cloned headers, updated with the authorization.
    // const authReq: HttpRequest<any> = req.clone({
    //     headers: req.headers.append("Authorization", authToken)
    // });

    // // send cloned request with header to the next handler.
    // return next(authReq);
    return next(req);
};
