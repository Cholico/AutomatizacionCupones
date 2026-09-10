from string import Template

MENSAJE_CORREO = Template("""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tu Cupón Dolphy</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f7; color: #333333; margin: 0; padding: 20px;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" max-width="600px" style="background-color: #ffffff; border-radius: 8px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" cellspacing="0" cellpadding="0" border="0">
                    
                    <!-- Encabezado / Saludo -->
                    <tr>
                        <td style="font-size: 20px; font-weight: bold; color: #0056b3; padding-bottom: 15px;">
                            ¡Hola, ${nombre}! 🐬
                        </td>
                    </tr>

                    <!-- Contenido principal -->
                    <tr>
                        <td style="font-size: 15px; line-height: 1.6; color: #4a4a4a; padding-bottom: 20px;">
                            Te compartimos tu cupón para un delicioso <b>${producto}</b> 🍦.
                        </td>
                    </tr>

                    <!-- Tarjeta del Cupón / QR (Si adjuntas el QR en el correo con cid:qr_image_cid) -->
                    <tr>
                        <td align="center" style="background-color: #eef6ff; border-left: 4px solid #0056b3; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
                            <p style="margin: 0; font-size: 14px; color: #0056b3;"><b>Vigencia del cupón:</b></p>
                            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">${fecha_vigencia}</p>
                            
                            <!-- Imagen del QR si usas la incrustación cid -->
                            <div style="margin-top: 15px;">
                                <img src="cid:qr_image_cid" alt="Código QR Cupón" style="max-width: 180px; height: auto;" />
                            </div>
                        </td>
                    </tr>

                    <!-- Instrucciones -->
                    <tr>
                        <td style="font-size: 15px; line-height: 1.6; color: #4a4a4a; padding-top: 20px; padding-bottom: 20px;">
                            Para activar tu cupón, por favor responde a este correo con la palabra: <b>Recibido</b>.<br><br>
                            ¡Disfrútalo! 🍦

                            Para descargar tu cupon preciona sobre la imagen y pulsa ver imagen después te vas a los 3 puntos y le das descargar imagen y listo ya lo tienes en tu telefono o computadora.
                        </td>
                    </tr>

                    <!-- Línea divisoria -->
                    <tr>
                        <td style="border-top: 1px solid #e0e0e0; padding-top: 20px;"></td>
                    </tr>

                    <!-- Nota al pie / Soporte -->
                    <tr>
                        <td style="font-size: 12px; color: #777777; line-height: 1.5; background-color: #f9f9f9; padding: 12px; border-radius: 6px;">
                            <b>Nota:</b> Si tienes cualquier problema o duda con respecto a tu cupón, puedes responder directamente a este correo o escribir a <a href="mailto:acholico@heladosdolphy.com.mx" style="color: #0056b3; text-decoration: underline;">acholico@heladosdolphy.com.mx</a>.
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
""")
