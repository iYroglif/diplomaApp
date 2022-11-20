import { FormEvent, useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import User from "../../UserInterface";

interface LoginProps {
    setUser: (user: User) => void;
}

export default function Login({ setUser }: LoginProps) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loginError, setLoginError] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = useCallback(async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const response = await fetch('/api/login', {
            method: 'POST',
            body: new FormData(event.currentTarget)
        });

        if (response.ok) {
            const user = await response.json();
            setUser(user);
            navigate(-1);
        } else {
            setLoginError(true);
        }
    }, [navigate, setUser]);

    const formCorrect = username && password ? true : false;

    return (
        <>
            <form className="form-login" onSubmit={handleSubmit} onChange={() => setLoginError(false)}>
                <div className="form-group">
                    <label htmlFor="username">Имя пользователя</label>
                    <input className="form-control" type="text" id="username" name="username" value={username} onChange={(e) => setUsername(e.target.value)}></input>

                    <label htmlFor="password">Пароль</label>
                    <input className="form-control" type="password" id="password" name="password" value={password} onChange={(e) => setPassword(e.target.value)}></input>
                </div>
                <button className="button-login" type="submit" disabled={!formCorrect || loginError}>Войти</button>
            </form>
            {loginError && (<p>Неверный логин или пароль</p>)}
        </>
    );
}