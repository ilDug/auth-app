export class User {

    constructor(u: Partial<User>) {
        Object.assign(this, u);
    }

    id: string
    uid: string
    email: string
    username: string
    active: boolean
    authorizations: string[] = []
}