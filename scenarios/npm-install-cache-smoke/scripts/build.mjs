import { mkdir, writeFile } from 'node:fs/promises';
import { camelCase } from 'lodash-es';

const widgetLabel = camelCase('acme widget network smoke');

await mkdir('dist', { recursive: true });
await mkdir('artifacts', { recursive: true });

await writeFile('dist/index.js', `export const widgetLabel = ${JSON.stringify(widgetLabel)};\n`);
await writeFile('dist/index.d.ts', 'export declare const widgetLabel: string;\n');
await writeFile(
  'artifacts/install-report.json',
  JSON.stringify(
    {
      scenario: 'npm-install-cache-smoke',
      dependency: 'lodash-es@4.17.21',
      widget_label: widgetLabel
    },
    null,
    2
  ) + '\n'
);
