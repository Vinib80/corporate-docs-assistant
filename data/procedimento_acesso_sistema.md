# PROCEDIMENTO PARA SOLICITAÇÃO DE ACESSO A SISTEMAS CORPORATIVOS

## 1. OBJETIVO DO PROCEDIMENTO
Este documento detalha as etapas, responsabilidades e controles necessários para a concessão, modificação e revogação de acessos aos sistemas de informação, redes e bancos de dados da nossa empresa. O objetivo é garantir que apenas pessoas autorizadas tenham o acesso necessário para o desempenho de suas funções (Princípio do Menor Privilégio), mitigando riscos de segurança da informação e garantindo a rastreabilidade das operações.

## 2. PÚBLICO-ALVO
Todos os colaboradores (CLT, estagiários, aprendizes), terceiros, consultores, auditores externos e prestadores de serviço que necessitem de acesso aos recursos tecnológicos e sistemas de informação de propriedade ou sob gestão da empresa.

## 3. PAPÉIS E RESPONSABILIDADES

### 3.1. Solicitante
* Requisitar acessos necessários estritamente para a execução de suas atividades profissionais.
* Guardar sigilo de suas credenciais de acesso, não compartilhando senhas em nenhuma hipótese.
* Assinar o Termo de Sigilo e Responsabilidade antes de receber o primeiro acesso.
* Informar ao gestor caso note permissões além das necessárias.

### 3.2. Gestor Imediato (Aprovador)
* Avaliar e aprovar ou reprovar as solicitações de acesso de seus liderados.
* Garantir que as solicitações estejam alinhadas com as funções do cargo do colaborador.
* Notificar a equipe de TI/Segurança imediatamente em caso de desligamento, mudança de área ou afastamento prolongado do colaborador.
* Participar ativamente das campanhas de recertificação de acessos.

### 3.3. Equipe de TI / Gestão de Identidade e Acessos (IAM)
* Criar, modificar ou excluir perfis de acesso conforme fluxo de aprovação.
* Manter o catálogo de perfis de acesso (Roles) atualizado.
* Garantir que as aprovações ocorram no sistema de chamados oficial, mantendo trilha de auditoria.

### 3.4. Segurança da Informação (InfoSec)
* Monitorar tentativas de acesso anômalas e realizar auditorias de privilégios.
* Definir e aprovar o provisionamento de credenciais de acesso privilegiado (Administradores de rede, DBAs).
* Auditar os processos de concessão e revogação, avaliando indicadores e SLAs.

## 4. CLASSIFICAÇÃO DOS TIPOS DE ACESSO

* **Acesso Básico:** Pacote padrão fornecido no momento da contratação. Inclui e-mail corporativo, acesso à intranet, pacote Office básico e rede Wi-Fi corporativa (perfil usuário).
* **Acesso Específico de Negócio:** Sistemas departamentais, ERPs (ex: módulo de faturamento, folha de pagamento), CRMs, e pastas de rede compartilhadas. Exige aprovação direta do Gestor da Área.
* **Acesso Privilegiado (Admin):** Acesso a servidores, bancos de dados em produção, firewalls, switches e painéis de administração cloud. Exige aprovação do Gestor da Área, do Gestor de TI e da equipe de Segurança da Informação.
* **Acesso Temporário:** Concedido para auditores e consultores por tempo predeterminado, com data de expiração obrigatória configurada no sistema.

## 5. FLUXO DE SOLICITAÇÃO DE ACESSO (PASSO A PASSO)

### Passo 1: Abertura do Chamado (Ticket)
O solicitante ou o RH (no caso de novas contratações) deve acessar o Portal de Serviços de TI e selecionar o formulário de "Solicitação de Acesso". O formulário deve conter:
* Nome completo e matrícula do usuário.
* Cargo, departamento e centro de custo.
* Nome do sistema e/ou recurso solicitado.
* Nível de acesso/perfil desejado.
* Justificativa de negócio para o acesso.

### Passo 2: Aprovação Gerencial
O ticket é roteado automaticamente para a fila de aprovação do Gestor Imediato do solicitante, que deve avaliar a necessidade técnica e de negócio. Em caso de recusa, o ticket é encerrado.

### Passo 3: Aprovação de Segurança (se aplicável)
Para perfis de Acesso Privilegiado, após a aprovação do gestor, o ticket segue para a fila da área de Segurança da Informação. A análise verificará se há conflito de segregação de funções (SoD - Segregation of Duties).

### Passo 4: Provisionamento
Com as aprovações concluídas, a equipe de Gestão de Identidades e Acessos (IAM) realiza a liberação no sistema correspondente. O SLA para atendimento varia conforme o tipo de acesso:
* Acesso Básico: até 24 horas úteis.
* Acesso Específico de Negócio: até 48 horas úteis.
* Acesso Privilegiado: até 72 horas úteis.

### Passo 5: Encerramento e Notificação
A equipe de IAM notifica o usuário via sistema de chamados, fornecendo credenciais temporárias (caso aplicável) e orientando sobre o primeiro acesso. O usuário valida o acesso e encerra o chamado.

## 6. REVISÃO DE ACESSOS (RECERTIFICAÇÃO)

Para garantir a conformidade contínua, a empresa realiza campanhas de recertificação de acessos de acordo com a periodicidade abaixo:
* **Sistemas Críticos e Acessos Privilegiados:** Recertificação Trimestral.
* **Sistemas de Negócio Financeiros/Contábeis:** Recertificação Semestral.
* **Demais Sistemas Departamentais:** Recertificação Anual.
Durante a campanha, os gestores receberão um relatório listando todos os acessos ativos de seus liderados. O gestor deverá revisar e confirmar se o acesso deve ser "Mantido" ou "Revogado". O não cumprimento do prazo de revisão pelos gestores resultará no bloqueio temporário dos acessos dos colaboradores sob sua gestão.

## 7. REVOGAÇÃO DE ACESSO

### 7.1. Desligamento (Offboarding)
Ao ocorrer a rescisão do contrato de trabalho, o RH abre automaticamente um chamado de "Desligamento" para a área de TI.
* Acessos críticos são desativados imediatamente após o aviso prévio indenizado ou no final do expediente do último dia de trabalho.
* As caixas de e-mail e arquivos corporativos são mantidos bloqueados por 90 dias antes da exclusão definitiva, período no qual o gestor pode solicitar backup se estritamente necessário.

### 7.2. Transferências Internas
Quando um colaborador muda de cargo ou departamento, o acesso relacionado ao cargo anterior será revogado após um período de transição (máximo de 15 dias). O gestor da nova área deve solicitar os novos acessos adequados à nova função.

## 8. REGISTROS E TRILHAS DE AUDITORIA (LOGS)
Todos os sistemas abrangidos por esta política devem manter logs imutáveis detalhando:
* Quem acessou (ID de usuário).
* Quando acessou (Data e Hora com sincronismo NTP).
* De onde acessou (Endereço IP).
* O que acessou/modificou (Ações realizadas no sistema).
Estes logs serão retidos por, no mínimo, 12 (doze) meses para fins de auditoria interna, auditoria externa ou investigações forenses.

## 9. TRATAMENTO DE EXCEÇÕES
Qualquer solicitação que não possa seguir as diretrizes descritas neste documento será tratada como exceção. Exceções requerem o preenchimento do formulário "Risco Aceito", com assinatura conjunta do Diretor da Área solicitante e do Diretor de Tecnologia (CTO). As exceções terão validade máxima de 6 (seis) meses, devendo ser regularizadas após esse período.
