/**
 * Formato numérico en español: coma decimal y espacio fino como separador de miles,
 * como en las publicaciones del INEI y en las tablas de la tesis.
 */
const ESPACIO = ' ';

export function decimal(valor: number | null | undefined, decimales = 1): string {
  if (valor === null || valor === undefined || Number.isNaN(valor)) return '—';
  const [entero, fraccion] = Math.abs(valor).toFixed(decimales).split('.');
  const miles = entero.replace(/\B(?=(\d{3})+(?!\d))/g, ESPACIO);
  const signo = valor < 0 && Number(valor.toFixed(decimales)) !== 0 ? '−' : '';
  return signo + (fraccion ? `${miles},${fraccion}` : miles);
}

export const entero = (valor: number | null | undefined) => decimal(valor, 0);

/** Valor ya expresado en porcentaje (27.6 → "27,6 %"). */
export const porcentaje = (valor: number | null | undefined, decimales = 1) =>
  `${decimal(valor, decimales)}${ESPACIO}%`;

/** Proporción entre 0 y 1 (0.69 → "69,0 %"). */
export const proporcion = (valor: number | null | undefined, decimales = 1) =>
  valor === null || valor === undefined ? '—' : porcentaje(valor * 100, decimales);

/** Diferencia en puntos porcentuales con signo explícito. */
export function puntos(valor: number | null | undefined, decimales = 1): string {
  if (valor === null || valor === undefined) return '—';
  const signo = valor > 0 && Number(valor.toFixed(decimales)) !== 0 ? '+' : '';
  return `${signo}${decimal(valor, decimales)}${ESPACIO}pp`;
}

/** Millones de personas con un decimal (7 071 114 → "7,1 millones"). */
export const millones = (valor: number) => `${decimal(valor / 1e6, 1)} millones`;
