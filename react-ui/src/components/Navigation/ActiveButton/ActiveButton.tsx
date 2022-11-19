import { NavLink } from "react-router-dom";
import ButtonProps from "../Button/ButtonPropsInterface";
import "./ActiveButton.css";

export default function ActiveButton({ name, link, className }: ButtonProps) {
    return (
        <NavLink className={({ isActive }) =>
            isActive ? "button " + className + " active" : "button " + className
        } to={link}>
            {name}
        </NavLink>
    );
}