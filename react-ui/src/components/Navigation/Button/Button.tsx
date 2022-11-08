import { Link } from "react-router-dom";
import ButtonProps from "./ButtonPropsInterface";

export default function Button({ name, link, className }: ButtonProps) {
    return (
        <Link className="link" to={link}>
            <div className={className}>{name}</div>
        </Link>
    );
}