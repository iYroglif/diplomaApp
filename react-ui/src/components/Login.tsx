import React, { useEffect, useState } from "react";
import "./Login.css"

export const Login = () => {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [formCorrect, setFormCorrect] = useState(false)
    const [loginError, setLoginError] = useState(false)

    useEffect(() => {
        if (username && password) setFormCorrect(true)
        else setFormCorrect(false)
    }, [username, password])

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        fetch('/api/login', {
            method: 'POST',
            body: new FormData(event.currentTarget)
        }).then((res) => {
            if (res.ok)
                document.location.href = "/"
            else setLoginError(true)
        })
    }

    return (
        <>
            <form className="form-log" onSubmit={handleSubmit} onChange={() => setLoginError(false)}>
                <div className="form-group">
                    <label htmlFor="username">Имя пользователя</label>
                    <input className="form-control" type="text" id="username" name="username" value={username} onChange={(e) => setUsername(e.target.value)}></input>
                    <label htmlFor="password">Пароль</label>
                    <input className="form-control" type="password" id="password" name="password" value={password} onChange={(e) => setPassword(e.target.value)}></input>
                </div>
                <button className="btn btn-success btn-log" type="submit" disabled={!formCorrect || loginError}>Войти</button>
            </form>
            {loginError && (<p>Неверный логин или пароль</p>)}
        </>
    );
}