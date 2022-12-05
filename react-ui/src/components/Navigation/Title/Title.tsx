import { Link } from "react-router-dom";
import "./Title.css";

export const Title = () => {
  return (
    <Link className="title-nav" to="/">
      <h1>Веб-приложение</h1>
    </Link>
  );
};
