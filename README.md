# Instruções para instalação do script

Para rodar o script no ubuntu é necessário instalar os pacotes lxml, tabulate e pandas

```console
apt install python3-tabulate python3-pandas python3-lxml
```

Dependendo de como você copiou os arquivos é necesário torná-los executáveis para facilitar o seu uso.

```console
chmod +x sheetToFet.py
chmod +x addRestrictions.py
```

# Uso do script

Para uso do script você precisará gerar um link público (para leitura) da planilha do googlesheets. No link gerado você precisará extrair o código da planilha. Por exemplo, no link

https://docs.google.com/spreadsheets/d/1Aq7Kbq0Eg8NGSueGPdfeHwn6Fe-zmd2DIP5cvYkG7e0/edit?usp=sharing

o código da planilha é 1Aq7Kbq0Eg8NGSueGPdfeHwn6Fe-zmd2DIP5cvYkG7e0.

O arquivo inicial com as atividades pode ser gerado pelo comando.

./sheetToFet.py -o NOME_DO_ARQUIVO_A_SER_GERADO.fet -code CODIGO_DA_PLANILHA_GOOGLE

As restrições adicionais podem ser inseridas no arquivo usando o segundo script

./addRestrictions.py -i ARQUIVO_DE_ENTRADA.fet -o ARQUIVO_DE_SAIDA.fet -code CODIGO_DA_PLANILHA_GOOGLE


