import { Link } from "react-router-dom";
import ButtonProps from "./ButtonPropsInterface";
import "./Button.css";

export default function Button({ name, link, className }: ButtonProps) {
    return (
        <Link className={"button " + className} to={link}>
            {name}
        </Link>
    );
}