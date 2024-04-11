from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

@task
def order_robots_from_RobotSpareBin():
    browser.configure(
        slowmo = 1000,
    )
    abrir_site_de_pedidos()
    baixar_csv()
    preencher_com_dados_csv()
    arquivos_detalhes()
    clean_up()

def abrir_site_de_pedidos():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    page = browser.page()
    page.click("button:text('OK')")

def baixar_csv():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv")

def realizar_outro_pedido():
    page = browser.page()
    page.click("#order-another")

def clicar_ok():
    page = browser.page()
    page.click("button:text('OK')")

def preencher_dados_robo(pedido):
    page = browser.page()
    nome_head = {
        "1" : "Roll-a-thor head",
        "2" : "Peanut crusher head",
        "3" : "D.A.V.E head",
        "4" : "Andy Roid head",
        "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"
    }
    num_head = pedido["Head"]
    page.select_option("#head", nome_head.get(num_head))
    page.click('//*[@id="root"]/div/div[1]/div/div[1]/form/div[2]/div/div[{0}]/label'.format(pedido["Body"]))
    page.fill("input[placeholder='Enter the part number for the legs']", pedido["Legs"])
    page.fill("#address", pedido["Address"])
    while True:
        page.click("#order")
        pedir_outro = page.query_selector("#order-another")
        if pedir_outro:
            local_pdf = exportar_detalhes_pdf(int(pedido["Order number"]))
            local_prt = printar_robo(int(pedido["Order number"]))
            integrar_prt_detalhes(local_prt, local_pdf)
            realizar_outro_pedido()
            clicar_ok()
            break

def exportar_detalhes_pdf(num_pedido):
    page = browser.page()
    detalhes_pedido_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    local_pdf = "output/receipts/{0}.pdf".format(num_pedido)
    pdf.html_to_pdf(detalhes_pedido_html, local_pdf)
    return local_pdf

def preencher_com_dados_csv():
    arquivo_csv = Tables()
    pedidos_robos = arquivo_csv.read_table_from_csv("orders.csv")
    for pedido in pedidos_robos:
        preencher_dados_robo(pedido)

def printar_robo(num_pedido):
    page = browser.page()
    local_prt = "output/screenshots/{0}.png".format(num_pedido)
    page.locator("#robot-preview-image").screenshot(path=local_prt)
    return local_prt

def integrar_prt_detalhes(local_prt, local_pdf):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=local_prt, source_path=local_pdf, output_path=local_pdf)

def arquivos_detalhes():
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")

def clean_up():
    shutil.rmtree("./output/receipts")
    shutil.rmtree("./output/screenshots")