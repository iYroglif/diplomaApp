import { ChangeEvent, FormEvent, useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import { User } from "../../UserInterface";
import { loginURL } from "../../api/urls";

interface LoginProps {
  setUser: (user: User) => void;
}

export const Login = ({ setUser }: LoginProps) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState(false);
  const navigate = useNavigate();

  const formCorrect = username && password ? true : false;

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      const response = await fetch(loginURL, {
        method: "POST",
        body: new FormData(event.currentTarget),
      });

      if (response.ok) {
        const user = await response.json();
        setUser(user);
        navigate("/");
      } else {
        setLoginError(true);
      }
    },
    [navigate, setUser]
  );

  const handleFormChange = useCallback(() => {
    setLoginError(false);
  }, []);

  const handleUsernameChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setUsername(event.target.value);
  }, []);

  const handlePasswordChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setPassword(event.target.value);
  }, []);

  return (
    <>
      <form className="form-login" onSubmit={handleSubmit} onChange={handleFormChange}>
        <div className="form-group">
          {[
            { id: "username", text: "Имя пользователя", type: "text", name: "username", value: username, onChange: handleUsernameChange },
            { id: "password", text: "Пароль", type: "password", name: "password", value: password, onChange: handlePasswordChange },
          ].map(({ id, text, type, name, value, onChange }) => (
            <>
              <label htmlFor={id}>{text}</label>
              <input className="form-control" type={type} id={id} name={name} value={value} onChange={onChange}></input>
            </>
          ))}
        </div>

        <button className="button-login" type="submit" disabled={!formCorrect || loginError}>
          Войти
        </button>
      </form>
      {loginError && <p>Неверный логин или пароль</p>}
    </>
  );
};
