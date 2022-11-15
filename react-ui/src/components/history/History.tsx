import { TaskRow } from "./TaskRow";
import "./History.css";
import TaskRowProps from "./TaskRowPropsInterface";
import useFetchJSON from "../../useFetchJSON";

export default function History() {
    const [data, error] = useFetchJSON<{ tasks: [] }>('/api/history');

    let rows: JSX.Element[] = [];

    if (!error && data !== null) {
        rows = data.tasks.map((row: TaskRowProps) => {
            return <TaskRow key={row.id} {...row} />;
        });
    }

    return (
        <div className="history">
            <table className="table">
                <thead className="table table-striped">
                    <tr>
                        <th scope="col">Название файла</th>
                        <th scope="col">Размер</th>
                        <th scope="col">Дата и время</th>
                        <th scope="col"></th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    );
}