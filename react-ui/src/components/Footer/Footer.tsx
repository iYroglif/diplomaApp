import "./Footer.css";

export const Footer = () => {
  return (
    <footer>
      {[
        { className: "vkrb", text: "Выпускная квалификационная работа бакалавра" },
        { className: "mgtu", text: "МГТУ им. Н. Э. Баумана. Кафедра ИУ5" },
        { className: "author", text: "Терентьев В.О. ИУ5-83Б 2022" },
      ].map(({ className, text }) => (
        <div className={className}>{text}</div>
      ))}
    </footer>
  );
};
