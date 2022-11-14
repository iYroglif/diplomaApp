import { FormEvent, useCallback, useState } from "react";
import "./Register.css";

export default function Register() {
    const [userName, setUserName] = useState('');
    const [firstPassword, setFirstPassword] = useState('');
    const [secondPassword, setSecondPassword] = useState('');
    const [registerError, setRegisterError] = useState(false);

    const handleSubmit = useCallback(async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const response = await fetch('/api/register', {
            method: 'POST',
            body: new FormData(event.currentTarget)
        });

        if (response.ok) {
            document.location.href = "/";
        } else {
            setRegisterError(true);
        }
    }, []);

    const formCorrect = userName && firstPassword && firstPassword === secondPassword ? true : false;

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
                    <input className="form-control" type="password" id="password" name="password" value={firstPassword} onChange={(e) => setFirstPassword(e.target.value)}></input>

                    <label htmlFor="check_password">Повторите пароль</label>
                    <input className="form-control" type="password" id="check_password" value={secondPassword} onChange={(e) => setSecondPassword(e.target.value)}></input>
                </div>
                <button className="btn btn-success btn-reg" type="submit" disabled={registerError || !formCorrect}>Зарегистрироваться</button>
            </form>
            {registerError && (<p>Данное имя пользователя уже занято. Введите другое</p>)}
        </>
    );
}
