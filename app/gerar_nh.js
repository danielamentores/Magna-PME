// gerar_nh.js — recebe JSON path e output path como args
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, ShadingType, VerticalAlign,
} = require('docx');
const fs = require('fs');

const jsonPath = process.argv[2];
const outPath  = process.argv[3];
const dados    = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));

const fmtEur = (v) => Number(v).toFixed(2).replace('.', ',') + ' €';
const cor_header    = "1F4E79";
const cor_subheader = "2E75B6";
const cor_row_alt   = "EBF3FB";
const border    = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders   = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function headerCell(text, width, colspan) {
  return new TableCell({ borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: cor_header, type: ShadingType.CLEAR }, margins: cellMargins,
    columnSpan: colspan || 1,
    children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 20, font: "Arial" })] })] });
}

function subHeaderCell(text, width, colspan) {
  return new TableCell({ borders, width: { size: width, type: WidthType.DXA },
    shading: { fill: cor_subheader, type: ShadingType.CLEAR }, margins: cellMargins,
    columnSpan: colspan || 1,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 18, font: "Arial" })] })] });
}

function labelCell(label, value, width) {
  return new TableCell({ borders, width: { size: width, type: WidthType.DXA }, margins: cellMargins,
    children: [new Paragraph({ children: [
      new TextRun({ text: label + ": ", bold: true, size: 18, font: "Arial" }),
      new TextRun({ text: value, size: 18, font: "Arial" })
    ] })] });
}

function dataCell(text, width, align, bold, shade) {
  return new TableCell({ borders, width: { size: width, type: WidthType.DXA }, margins: cellMargins,
    shading: shade ? { fill: cor_row_alt, type: ShadingType.CLEAR } : undefined,
    children: [new Paragraph({ alignment: align || AlignmentType.LEFT,
      children: [new TextRun({ text: String(text), bold: bold || false, size: 18, font: "Arial" })] })] });
}

const volumeTotal = dados.acoes.reduce((s, a) => s + (a.ch * a.formandos), 0);

const doc = new Document({
  styles: { default: { document: { run: { font: "Arial", size: 20 } } } },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838 },
    margin: { top: 720, right: 720, bottom: 720, left: 720 } } },
    children: [

      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
        children: [new TextRun({ text: "Registo de Honorários", bold: true, size: 32, font: "Arial", color: cor_header })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
        children: [new TextRun({ text: "Entidade Formadora | Consultor Externo", size: 22, font: "Arial", color: "444444" })] }),

      new Table({ width: { size: 10466, type: WidthType.DXA }, columnWidths: [3488, 3489, 3489],
        rows: [new TableRow({ children: [
          labelCell("NH Nº", String(dados.nh_numero), 3488),
          labelCell("Parceiro", dados.consultor.nome, 3489),
          labelCell("Projeto", `${dados.projeto.nome} (${dados.projeto.codigo})`, 3489),
        ]})] }),

      new Paragraph({ spacing: { after: 160 }, children: [] }),

      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun({ text: "Condições de pagamento", bold: true, size: 22, font: "Arial", color: cor_header })] }),
      new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: cor_subheader } }, spacing: { after: 120 },
        children: [new TextRun({ text: dados.condicoes, size: 18, font: "Arial" })] }),

      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun({ text: "Dados para emissão do recibo", bold: true, size: 22, font: "Arial", color: cor_header })] }),
      new Table({ width: { size: 10466, type: WidthType.DXA }, columnWidths: [1746, 8720],
        rows: [
          new TableRow({ children: [ labelCell("NIF", dados.destinatario.nif, 1746), labelCell("Nome", dados.destinatario.nome, 8720) ] }),
          new TableRow({ children: [ labelCell("Morada", dados.destinatario.morada, 1746),
            new TableCell({ borders, width: { size: 8720, type: WidthType.DXA }, margins: cellMargins,
              children: [new Paragraph({ children: [new TextRun({ text: dados.destinatario.morada, size: 18, font: "Arial" })] })] }) ] }),
          new TableRow({ children: [ labelCell("Descritivo", "", 1746),
            new TableCell({ borders, width: { size: 8720, type: WidthType.DXA }, margins: cellMargins,
              children: [new Paragraph({ children: [new TextRun({ text: dados.descritivo, size: 18, font: "Arial", italics: true })] })] }) ] }),
        ] }),

      new Paragraph({ spacing: { after: 160 }, children: [] }),

      new Table({ width: { size: 10466, type: WidthType.DXA }, columnWidths: [10466],
        rows: [
          new TableRow({ children: [ subHeaderCell("Dados da Entidade Consultora / Comercial", 10466) ] }),
          new TableRow({ children: [ new TableCell({ borders, width: { size: 10466, type: WidthType.DXA }, margins: cellMargins,
            children: [new Paragraph({ children: [new TextRun({ text: "Nome: ", bold: true, size: 18, font: "Arial" }), new TextRun({ text: dados.consultor.nome, size: 18, font: "Arial" })] })] }) ] }),
          new TableRow({ children: [ new TableCell({ borders, width: { size: 10466, type: WidthType.DXA }, margins: cellMargins,
            children: [new Paragraph({ children: [
              new TextRun({ text: "Certificada pela DGERT: ", bold: true, size: 18, font: "Arial" }), new TextRun({ text: dados.consultor.dgert + "   ", size: 18, font: "Arial" }),
              new TextRun({ text: "NIF: ", bold: true, size: 18, font: "Arial" }), new TextRun({ text: dados.consultor.nif + "   ", size: 18, font: "Arial" }),
              new TextRun({ text: "Enq. Fiscal: ", bold: true, size: 18, font: "Arial" }), new TextRun({ text: `IVA: ${dados.consultor.iva}  IRS: ${dados.consultor.irs}`, size: 18, font: "Arial" }),
            ] })] }) ] }),
          new TableRow({ children: [ new TableCell({ borders, width: { size: 10466, type: WidthType.DXA }, margins: cellMargins,
            children: [new Paragraph({ children: [
              new TextRun({ text: "Morada: ", bold: true, size: 18, font: "Arial" }), new TextRun({ text: dados.consultor.morada + "   ", size: 18, font: "Arial" }),
              new TextRun({ text: "Código Postal: ", bold: true, size: 18, font: "Arial" }), new TextRun({ text: dados.consultor.cod_postal + "   ", size: 18, font: "Arial" }),
              new TextRun({ text: "Localidade: ", bold: true, size: 18, font: "Arial" }), new TextRun({ text: dados.consultor.localidade, size: 18, font: "Arial" }),
            ] })] }) ] }),
          new TableRow({ children: [ new TableCell({ borders, width: { size: 10466, type: WidthType.DXA }, margins: cellMargins,
            children: [new Paragraph({ children: [new TextRun({ text: "IBAN: ", bold: true, size: 18, font: "Arial" }), new TextRun({ text: dados.consultor.iban, size: 18, font: "Arial" })] })] }) ] }),
        ] }),

      new Paragraph({ spacing: { after: 160 }, children: [] }),

      new Table({ width: { size: 10466, type: WidthType.DXA }, columnWidths: [3266, 1400, 700, 1000, 1400, 900, 900, 900],
        rows: [
          new TableRow({ children: [ subHeaderCell("Identificação e Valores a Pagar", 10466, 8) ] }),
          new TableRow({ children: [
            headerCell("Código / Serviço", 3266), headerCell("Data Inicial e Final", 1400), headerCell("Volume", 700),
            headerCell("Valor p/ Volume", 1000), headerCell("Valor Base", 1400), headerCell("IVA", 900), headerCell("IRS", 900), headerCell("Valor Líquido", 900),
          ] }),
          new TableRow({ children: [
            dataCell(dados.descritivo, 3266),
            dataCell(`${dados.data_inicial} a ${dados.data_final}`, 1400, AlignmentType.CENTER),
            dataCell(String(volumeTotal), 700, AlignmentType.CENTER),
            dataCell("—", 1000, AlignmentType.CENTER),
            dataCell(fmtEur(dados.valor_base), 1400, AlignmentType.RIGHT, true),
            dataCell(fmtEur(dados.iva_valor), 900, AlignmentType.RIGHT),
            dataCell(fmtEur(dados.irs_valor), 900, AlignmentType.RIGHT),
            dataCell(fmtEur(dados.valor_liquido), 900, AlignmentType.RIGHT, true),
          ] }),
        ] }),

      new Paragraph({ spacing: { after: 160 }, children: [] }),

      new Table({ width: { size: 10466, type: WidthType.DXA }, columnWidths: [2200, 1400, 2400, 700, 700, 600, 700, 1766],
        rows: [
          new TableRow({ children: [ subHeaderCell("Ações de formação terminadas na Magna e em reembolso", 10466, 8) ] }),
          new TableRow({ children: [
            headerCell("Empresa", 2200), headerCell("Operação", 1400), headerCell("UFCD / Descrição", 2400),
            headerCell("Início", 700), headerCell("Final", 700), headerCell("C.H.", 600), headerCell("Form.", 700), headerCell("Valor (Entidade/Coord.)", 1766),
          ] }),
          ...dados.acoes.map((a, i) => new TableRow({ children: [
            dataCell(a.empresa, 2200, AlignmentType.LEFT, false, i%2===1),
            dataCell(a.operacao, 1400, AlignmentType.LEFT, false, i%2===1),
            dataCell(a.ufcd, 2400, AlignmentType.LEFT, false, i%2===1),
            dataCell(a.inicio, 700, AlignmentType.CENTER, false, i%2===1),
            dataCell(a.fim, 700, AlignmentType.CENTER, false, i%2===1),
            dataCell(a.ch, 600, AlignmentType.CENTER, false, i%2===1),
            dataCell(a.formandos, 700, AlignmentType.CENTER, false, i%2===1),
            dataCell(fmtEur(a.valor), 1766, AlignmentType.RIGHT, true, i%2===1),
          ] })),
          new TableRow({ children: [
            new TableCell({ borders, columnSpan: 7, width: { size: 8700, type: WidthType.DXA }, margins: cellMargins,
              shading: { fill: cor_header, type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.RIGHT,
                children: [new TextRun({ text: "TOTAL", bold: true, color: "FFFFFF", size: 20, font: "Arial" })] })] }),
            new TableCell({ borders, width: { size: 1766, type: WidthType.DXA }, margins: cellMargins,
              shading: { fill: cor_header, type: ShadingType.CLEAR },
              children: [new Paragraph({ alignment: AlignmentType.RIGHT,
                children: [new TextRun({ text: fmtEur(dados.valor_liquido), bold: true, color: "FFFFFF", size: 20, font: "Arial" })] })] }),
          ] }),
        ] }),

      new Paragraph({ spacing: { after: 400 }, children: [] }),
      new Paragraph({ spacing: { after: 80 },
        children: [new TextRun({ text: "Confirmo que li e confirmei que os dados do formador/colaborador estão corretos.", size: 18, font: "Arial", italics: true })] }),
      new Paragraph({ children: [
        new TextRun({ text: "Assinatura: ", bold: true, size: 18, font: "Arial" }),
        new TextRun({ text: "_______________________________________", size: 18, font: "Arial" }),
      ] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => { fs.writeFileSync(outPath, buf); console.log('OK'); });
