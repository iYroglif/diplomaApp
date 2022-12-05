import { FormEvent, useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerURL } from "../../api/urls";
import { User } from "../../UserInterface";
import "./Register.css";

interface RegisterProps {
  setUser: (user: User) => void;
}

export const Register = ({ setUser }: RegisterProps) => {
  const [userName, setUserName] = useState("");
  const [firstPassword, setFirstPassword] = useState("");
  const [secondPassword, setSecondPassword] = useState("");
  const [registerError, setRegisterError] = useState(false);
  const navigate = useNavigate();

  const formCorrect = userName && firstPassword && firstPassword === secondPassword ? true : false;

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      const response = await fetch(registerURL, {
        method: "POST",
        body: new FormData(event.currentTarget),
      });

      if (response.ok) {
        const user = await response.json();
        setUser(user);
        navigate("/");
      } else {
        setRegisterError(true);
      }
    },
    [navigate, setUser]
  );

  const handleUsernameChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setUserName(event.target.value);
  }, []);

  const handlePasswordChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setFirstPassword(event.target.value);
  }, []);

  const handleSecondPasswordChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    setSecondPassword(event.target.value);
  }, []);

  const setRegisterErrorToFalse = useCallback(() => {
    setRegisterError(false);
  }, []);

  return (
    <>
      <form className="form-registration" onSubmit={handleSubmit} onChange={setRegisterErrorToFalse}>
        <div className="form-group">
          {[
            { id: "username", text: "Имя пользователя", type: "text", name: "username", value: userName, onChange: handleUsernameChange },
            { id: "first_name", text: "Имя", type: "text", name: "first_name" },
            { id: "last_name", text: "Фамилия", type: "text", name: "last_name" },
            { id: "email", text: "Электронная почта", type: "email", name: "email" },
            { id: "password", text: "Пароль", type: "password", name: "password", value: firstPassword, onChange: handlePasswordChange },
            {
              id: "check_password",
              text: "Повторите пароль",
              type: "password",
              value: secondPassword,
              onChange: handleSecondPasswordChange,
            },
          ].map(({ id, text, type, name, value, onChange }) => (
            <>
              <label htmlFor={id}>{text}</label>
              <input className="form-control" type={type} id={id} name={name} value={value} onChange={onChange}></input>
            </>
          ))}
        </div>

        <button className="button-registration" type="submit" disabled={registerError || !formCorrect}>
          Зарегистрироваться
        </button>
      </form>
      {registerError && <p>Данное имя пользователя уже занято. Введите другое</p>}
    </>
  );
};
