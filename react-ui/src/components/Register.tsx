import React, { useEffect, useState } from "react";
import "./Register.css"

export const Register = () => {
    const [registerError, setRegisterError] = useState(false)
    const [userName, setUserName] = useState('')
    const [fPass, setFPass] = useState('')
    const [sPass, setSPass] = useState('')
    const [formCorrect, setFormCorrect] = useState(false)

    useEffect(() => {
        if (userName && fPass && fPass === sPass) setFormCorrect(true)
        else setFormCorrect(false)
    }, [userName, fPass, sPass])

    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()
        fetch('/api/register', {
            method: 'POST',
            body: new FormData(event.currentTarget)
        }).then((res) => {
            if (res.ok)
                document.location.href = "/"
            else setRegisterError(true)
        })
    }

    return (
        <>
            <form className="form-reg" onSubmit={handleSubmit} onChange={() => setRegisterError(false)}>
                <div className="form-group">
                    <label htmlFor="username">Имя пользователя</label>
                    <input className="form-control" type="text" id="username" name="username" value={userName} onChange={(e) => setUserName(e.target.value)}></input>

                    <label htmlFor="first_name">Имя</label>
                    <input className="form-control" type="text" id="first_name" name="first_name"></input>

                    <label htmlFor="last_name">Фамилия</label>
                    <input className="form-control" type="text" id="last_name" name="last_name"></input>

                    <label htmlFor="email">Электронная почта</label>
                    <input className="form-control" type="email" id="email" name="email"></input>

                    <label htmlFor="password">Пароль</label>
                    <input className="form-control" type="password" id="password" name="password" value={fPass} onChange={(e) => setFPass(e.target.value)}></input>

                    <label htmlFor="check_password">Повторите пароль</label>
                    <input className="form-control" type="password" id="check_password" value={sPass} onChange={(e) => setSPass(e.target.value)}></input>
                </div>
                <button className="btn btn-success btn-reg" type="submit" disabled={registerError || !formCorrect}>Зарегистрироваться</button>
            </form>
            {registerError && (<p>Данное имя пользователя уже занято. Введите другое</p>)}
        </>
    );
}
