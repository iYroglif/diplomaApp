import { TaskRow } from "./TaskRow";
import "./History.css";
import { TaskRowProps } from "./TaskRowPropsInterface";
import { useFetchJSON } from "../../useFetchJSON";
import { historyURL } from "../../api/urls";

export const History = () => {
  const [data, error] = useFetchJSON<{ tasks: [] }>(historyURL);

  let rows: JSX.Element[] = [];

  if (!error && data !== undefined) {
    rows = data.tasks.map((row: TaskRowProps) => {
      return <TaskRow key={row.id} {...row} />;
    });
  }

  return (
    <table className="history">
      <thead>
        <tr>
          {["Название файла", "Размер", "Дата и время", ""].map((text) => (
            <th scope="col">{text}</th>
          ))}
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
  );
};
