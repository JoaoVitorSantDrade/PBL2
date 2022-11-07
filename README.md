<h1> Consumo de Água Inteligente</h1>

<h2> Alisson Rodrigues¹ ,  João Victor² </h2>
<h2> {alissonrdcsantos, jvitorsantdrade}@gmail.com </h2>

<p><i><strong> Resumo.</strong>  Este relatório descreve a implementação do sistema de comunicação e controle de uma rede abastecimento de água, o sistema foi desenvolvido em linguagem de programação python utilizando os recursos disponibilizados, paho MQTT para comunicação entre processos, Threads e o framework Flash para construção de uma API Rest, visando atender as requisições de milhões de hidrômetros e acessos de usuários foi empregada uma arquitetura descentralizada usando computação em Nevoa. </i></p>

<h1>Introdução</h1>

<p>
 Problemas no abastecimento e distribuição de água são recorrentes no Brasil, distribuidoras são obrigadas a implementar racionamento e políticas de conscientização para os consumidores devido cenários de seca e estiagem nas áreas de reservatórios, desperdício produzido por consumidores e vazamentos nas tubulações, dado um sistema de porte quilométrico e com necessidade de controle em tempo real tem-se um cenário propício para uma solução de internet das coisas(Internet of Things, IoT) informatizando o trabalho do controle de abastecimento e fiscalização do consumo a partir de uma rede de hidrômetros inteligente.</p>
<p>
    No problema anterior foi desenvolvido o protótipo do hidrômetro inteligente para o a medição, envio de dados e bloqueio do consumo nas residências dos consumidores junto de uma API Rest como interface da aplicação. Visando atender as necessidades de uma cidade uma nova arquitetura deve ser construída para atender ao envio de dados de milhões de hidrômetros e possibilitar o acesso com menor tempo possível dos dados aos usuários finais que necessitam visualizar os hidrômetros com o maior consumo a fim de traçar a estratégias de controle que beneficiem a todos consumidores.</p>
<p>
    Se fez necessário buscar uma nova solução para rede pois, uma solução centralizada seria inviável a atender os requisitos de latência e sobrecarregar um único servidor central, foram exploradas soluções descentralizadas como computação em névoa e computação em borda para construção da solução visando usar métodos aplicados a IOT como por exemplo o messaging protocol for the Internet of Things MQTT a ser aplicado como protocolo de comunicação.</p>
<p>
    O restante deste relatório aborda o processo de desenvolvimento da solução do problema e foi organizado da seguinte forma. A seção 2 aborda a fundamentação teórica dos conceitos e tecnologias utilizadas na solução. A seção 3 apresenta a metodologia desenvolvida e os detalhes de implementação junto aos diagramas do sistema proposto. A seção 4 apresenta e discute os resultados obtidos. A seção 5 apresenta as conclusões sobre a solução projetada e conhecimentos adquiridos.
</p>
